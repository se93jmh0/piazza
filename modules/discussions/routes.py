"""Piazza's discussions-related API routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import models
import modules.discussions.models
import modules.discussions.schemas
from database import get_db
from security import get_current_user

router = APIRouter()


@router.post(
    "/posts",
    response_model=modules.discussions.schemas.DiscussionPost,
    status_code=201,
)
def create_discussion_post(
    post: modules.discussions.schemas.DiscussionPostCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> modules.discussions.schemas.DiscussionPost:
    """Create a discussion post."""

    db_post = modules.discussions.models.DiscussionPost(
        author_id=current_user.id,
        created_at=datetime.now(timezone.utc),
        title=post.title,
        body=post.body,
        expires_at=post.expires_at,
    )
    try:
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err))

    # Unfortunately TZ info is clobbered by the Session.refresh().
    db_post.created_at = db_post.created_at.astimezone(timezone.utc)
    db_post.expires_at = db_post.expires_at.astimezone(timezone.utc)

    return db_post
