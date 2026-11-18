"""Piazza's discussion-related SQLAlchemy database models."""

from datetime import datetime

from pydantic_core.core_schema import nullable_schema
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, PrimaryKeyConstraint

import models
from database import Base


class DiscussionPost(Base):
    """A Piazza discussion post."""

    __tablename__ = "discussion_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __author: Mapped[models.User] = relationship(models.User)
    author = property(lambda self: self.__author.email)

    __topics: Mapped[list["DiscussionPostTopic"]] = relationship(
        "DiscussionPostTopic"
    )
    topics = property(
        lambda self: [topic.topic.name for topic in self.__topics]
    )

    comments: Mapped[list["DiscussionPostComment"]] = relationship()


class DiscussionTopic(Base):
    """A Piazza discussion topic."""

    __tablename__ = "discussion_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class DiscussionPostTopic(Base):
    """Association of a Piazza discussion post with one of its topics."""

    __tablename__ = "discussion_post_topics"
    __table_args__ = (PrimaryKeyConstraint("post_id", "topic_id"),)

    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discussion_posts.id"), nullable=False
    )
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discussion_topics.id"), nullable=False
    )

    topic: Mapped["DiscussionTopic"] = relationship(DiscussionTopic)


class DiscussionPostComment(Base):
    """A comment on a Piazza discussion post."""

    __tablename__ = "discussion_post_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("discussion_posts.id"),
        nullable=False,
        back_populates="comments",
    )
    body: Mapped[str] = mapped_column(String, nullable=False)

    __author: Mapped[models.User] = relationship(models.User)
    author = property(lambda self: self.__author.email)


class DiscussionPostReaction(Base):
    """Reactions on a Piazza discussion post."""

    __tablename__ = "discussion_post_reactions"
    __table_args__ = (PrimaryKeyConstraint("post_id", "user_id"),)

    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discussion_posts.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    # 1 or 0.  But specifically integer for the purposes of SUM().
    like: Mapped[int] = mapped_column(Integer, default=0)
    # 1 or 0.  But specifically integer for the purposes of SUM().
    dislike: Mapped[int] = mapped_column(Integer, default=0)
