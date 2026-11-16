"""Piazza's discussions-related API routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

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
        db.flush()
        db.commit()

        db.expire_all()

        statement = select(models.DiscussionTopic).execution_options(
            populate_existing=True
        )
        db.execute(statement)

        statement = select(models.DiscussionPostTopic).execution_options(
            populate_existing=True
        )
        db.execute(statement)

        db_post_topics = [
            models.DiscussionPostTopic(post_id=db_post.id, topic_id=topic_id)
            for topic_id in topic_ids
        ]

        # db.add_all(db_post_topics)
        # db.flush()
        for db_post_topic in db_post_topics:
            print(db.get(models.DiscussionTopic, 1))
            db.add(db_post_topic)
            print(db.get(models.DiscussionTopic, 1))
            db.get(models.DiscussionTopic, 1)
            print(db.get(models.DiscussionTopic, 1))
            db.flush()
            print(db.get(models.DiscussionTopic, 1))
            db.commit()
            print(db.get(models.DiscussionTopic, 1))
            # db.refresh(db_post_topic.topic)
            db.expire_all()
            print(db.get(models.DiscussionTopic, 1))
            print(db_post_topic.topic)
            print(db.get(models.DiscussionTopic, 1))
            db.refresh(db_post_topic)
            print(db.get(models.DiscussionTopic, 1))
            db.merge(db_post_topic)
        db.merge(db_post)
        # db.merge(db_post)

    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err))

    statement = select(models.DiscussionTopic).execution_options(
        populate_existing=True
    )
    db.execute(statement)

    statement = select(models.DiscussionPostTopic).execution_options(
        populate_existing=True
    )
    db.execute(statement)

    # Unfortunately TZ info is clobbered by the Session.refresh().
    db_post.created_at = db_post.created_at.astimezone(timezone.utc)
    db_post.expires_at = db_post.expires_at.astimezone(timezone.utc)

    return db_post


@router.post(
    "/posts/{post_id}/comments",
    response_model=schemas.DiscussionPost,
    status_code=201,
)
def add_discussion_post_comment(
    post_id: int,
    post: schemas.DiscussionPostCommentAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DiscussionPost:
    """Add a comment on a discussion post."""

    db_comment = models.DiscussionPostComment(
        author_id=current_user.id,
        created_at=datetime.now(timezone.utc),
        body=post.body,
    )
    try:
        db.add(db_comment)
        db.commit()
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err))

    # Unfortunately TZ info is clobbered by the Session.refresh().
    db_comment.created_at = db_comment.created_at.astimezone(timezone.utc)

    return db_comment
