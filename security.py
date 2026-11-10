"""Security-related utility functionality."""

import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

import models
from database import get_db

SECRET_KEY = os.environ["JWT_SECRET"]
if len(SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET must contain at least 32 characters")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTPBearer tells FastAPI to expect an Authorization: Bearer <token> header.
bearer_scheme = HTTPBearer(auto_error=False)

# Use the recommended pwdlib hasher (currently, Argon2 with default params).
password_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash password using the default hasher."""

    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that the passwords match."""

    return password_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create a JWT with our configured secret and default expiry."""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Require JWT-based bearer auth on a FastAPI endpoint."""

    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        email = payload.get("sub")

        if not isinstance(email, str) or not email:
            raise HTTPException(status_code=401, detail="Invalid token")

    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
