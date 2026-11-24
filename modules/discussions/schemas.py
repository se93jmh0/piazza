"""Piazza's discussions-related Pydantic-based API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class DiscussionPostCreate(BaseModel):
    """Create a discussion post."""

    title: str
    body: str
    expires_at: datetime
    topics: list[str]


class DiscussionPost(BaseModel):
    """A discussion post."""

    id: int
    author: str
    created_at: datetime
    title: str
    body: str
    expires_at: datetime
    # status: str
    topics: list[str] = Field(validation_alias="topic_names")
    comments: list[DiscussionPostComment]
    likes: int
    dislikes: int


class DiscussionPostCommentAdd(BaseModel):
    """Add a comment on a discussion post."""

    body: str


class DiscussionPostComment(BaseModel):
    """A comment on a discussion post."""

    id: int
    author: str
    created_at: datetime
    post_id: int
    body: str


class DiscussionPostReaction(BaseModel):
    """React to a discussion post."""

    value: str


class DiscussionPostReactionCounts(BaseModel):
    """Like&Dislike counts for a discussion post."""

    post_id: int
    likes: int
    dislikes: int
