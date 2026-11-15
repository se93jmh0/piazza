"""Piazza's discussions-related Pydantic-based API schemas."""

from datetime import datetime

from pydantic import BaseModel


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
    topics: list[str]
