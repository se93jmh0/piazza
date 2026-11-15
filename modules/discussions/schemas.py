"""Piazza's discussions-related Pydantic-based API schemas."""

from datetime import datetime, timezone
from typing import Annotated

from pydantic import (
    AliasPath,
    BaseModel,
    BeforeValidator,
    Field,
    field_serializer,
)

from . import models


class DiscussionPostCreate(BaseModel):
    """Create a discussion post."""

    title: str
    body: str
    expires_at: datetime
    topics: list[str]


def from_model_topics(
    topics: list[models.DiscussionPostTopic],
) -> list[str]:
    """TODO."""
    return [topic.topic.name for topic in topics]


class DiscussionPost(BaseModel):
    """A discussion post."""

    def from_model_topics(
        self,
        topics: list[models.DiscussionPostTopic],
    ) -> list[str]:
        """TODO."""
        return [topic.topic.name for topic in topics]

    id: int
    author: str = Field(validation_alias=AliasPath("author", "email"))
    created_at: datetime
    title: str
    body: str
    expires_at: datetime
    topics: list[str]
