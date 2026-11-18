"""Piazza's discussions-related API routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions

from database import get_db
from models import User
from security import get_current_user

from . import models, schemas
from .topics_registry import TopicsRegistry

router = APIRouter()


@router.post(
    "/posts",
    response_model=schemas.DiscussionPost,
    status_code=201,
)
def create_discussion_post(
    post: schemas.DiscussionPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DiscussionPost:
    """Create a discussion post."""

    topic_ids = []
    for topic in post.topics:
        topic_id = TopicsRegistry.get_db_id(topic)
        if topic_id is None:
            raise HTTPException(
                status_code=422, detail=f"Unknown topic: '{topic}'"
            )
        topic_ids.append(topic_id)

    db_post = models.DiscussionPost(
        author_id=current_user.id,
        created_at=datetime.now(timezone.utc),
        title=post.title,
        body=post.body,
        expires_at=post.expires_at,
    )
    try:
        db.add(db_post)
        db.commit()

        db.add_all(
            models.DiscussionPostTopic(post_id=db_post.id, topic_id=topic_id)
            for topic_id in topic_ids
        )
        db.commit()

        db.flush()
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err))

    # Unfortunately TZ info is clobbered by the Session.refresh().
    db_post.created_at = db_post.created_at.astimezone(timezone.utc)
    db_post.expires_at = db_post.expires_at.astimezone(timezone.utc)

    return db_post


@router.post(
    "/posts/{post_id}/comments",
    response_model=schemas.DiscussionPostComment,
    status_code=201,
)
def add_discussion_post_comment(
    post_id: int,
    comment: schemas.DiscussionPostCommentAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DiscussionPostComment:
    """Add a comment on a discussion post."""

    db_post = db.get(models.DiscussionPost, post_id)
    if db_post == None:
        raise HTTPException(
            status_code=404, detail=f"Unknown post ID: {post_id}"
        )

    db_comment = models.DiscussionPostComment(
        author_id=current_user.id,
        created_at=datetime.now(timezone.utc),
        post_id=post_id,
        body=comment.body,
    )
    try:
        db.add(db_comment)
        db.commit()
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err))

    # Unfortunately TZ info is clobbered by the Session.refresh().
    db_comment.created_at = db_comment.created_at.astimezone(timezone.utc)

    return db_comment


@router.put(
    "/posts/{post_id}/reaction",
    response_model=schemas.DiscussionPostReactionCounts,
    status_code=200,
)
def react_to_discussion_post(
    post_id: int,
    reaction: schemas.DiscussionPostReaction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DiscussionPostReactionCounts:
    """React to a discussion post."""

    db_post = db.get(models.DiscussionPost, post_id)
    if db_post == None:
        raise HTTPException(
            status_code=404, detail=f"Unknown post ID: {post_id}"
        )

    db_reaction = models.DiscussionPostReaction(
        post_id=post_id,
        user_id=current_user.id,
    )
    if reaction.value == "like":
        db_reaction.like = 1
    elif reaction.value == "dislike":
        db_reaction.dislike = 1
    else:
        raise HTTPException(
            status_code=422, detail=f"Invalid reaction: '{reaction.value}'"
        )
    try:
        db.merge(db_reaction)
        db.commit()

        reactions = (
            db.query(
                functions.sum(models.DiscussionPostReaction.like),
                functions.sum(models.DiscussionPostReaction.dislike),
            )
            .where(models.DiscussionPostReaction.post_id == post_id)
            .first()
        )
        return schemas.DiscussionPostReactionCounts(
            post_id=post_id,
            # pyrefly: ignore
            likes=reactions[0],
            # pyrefly: ignore
            dislikes=reactions[1],
        )
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get(
    "/posts/{post_id}", response_model=schemas.DiscussionPost, status_code=200
)
def get_discussion_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DiscussionPost:
    """Get a discussion post."""

    try:
        db_post = db.get(
            models.DiscussionPost, post_id, populate_existing=True
        )
        if db_post == None:
            raise HTTPException(
                status_code=404, detail=f"Unknown post ID: {post_id}"
            )
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err))

    # Unfortunately TZ info is lost.  For reasons.
    db_post.created_at = db_post.created_at.astimezone(timezone.utc)
    db_post.expires_at = db_post.expires_at.astimezone(timezone.utc)

    return db_post
