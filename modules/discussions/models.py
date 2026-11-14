"""Piazza's discussion-related SQLAlchemy database models."""

from datetime import datetime

from pydantic_core.core_schema import nullable_schema
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

import models
from database import Base


class DiscussionPost(Base):
    """A Piazza discussion post."""

    __tablename__ = "discussion_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    author: Mapped[models.User] = relationship(models.User)


class DiscussionTopic(Base):
    """A Piazza discussion topic."""

    __tablename__ = "discussion_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
