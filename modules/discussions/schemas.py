"""Piazza's discussions-related Pydantic-based API schemas."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SkipValidation,
    model_validator,
)
from typing_extensions import Self


class DiscussionPostCreate(BaseModel):
    """Create a discussion post."""

    title: str
    body: str
    expires_at: datetime
    topics: list[str]


class DiscussionPost(BaseModel):
    """A discussion post."""

    # model_config = ConfigDict(from_attributes=True)

    id: int
    author: str
    created_at: datetime
    title: str
    body: str
    expires_at: datetime
    status: Annotated[str, SkipValidation]
    topics: list[str] = Field(validation_alias="topic_names")
    comments: list[DiscussionPostComment]
    likes: int
    dislikes: int

    @model_validator(mode="after")
    # pyrefly: ignore
    def noop_validation(self) -> Self:
        """TODO."""
        print("hi")
        return self


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
