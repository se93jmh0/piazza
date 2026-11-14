"""Piazza's discussions-related Pydantic-based API schemas."""

from datetime import datetime, timezone

from pydantic import AliasPath, BaseModel, Field, field_serializer


class DiscussionPostCreate(BaseModel):
    """Create a discussion post."""

    title: str
    body: str
    expires_at: datetime


class DiscussionPost(BaseModel):
    """A discussion post."""

    id: int
    author: str = Field(validation_alias=AliasPath("author", "email"))
    created_at: datetime
    title: str
    body: str
    expires_at: datetime
