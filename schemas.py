"""Piazza's Pydantic-based API schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Create a user."""

    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    """Log a user in."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User information."""

    id: int
    email: EmailStr


class TokenResponse(BaseModel):
    """User has successfully logged in."""

    access_token: str
    token_type: str
