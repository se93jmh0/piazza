"""Piazza's auth-related API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(
    user: schemas.UserCreate, db: Session = Depends(get_db)
) -> models.User:
    """Register a user."""

    existing_user = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    db_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    user_login: schemas.UserLogin, db: Session = Depends(get_db)
) -> models.User:
    """Log in a user."""

    user = (
        db.query(models.User)
        .filter(models.User.email == user_login.email)
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid email or password"
        )

    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Invalid email or password"
        )

    # Use the user's email as the Subject claim for the token.
    token = create_access_token({"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}


# Temporary API for proving that auth is working properly.
@router.get("/hiya")
def hiya(
    current_user: models.User = Depends(get_current_user),
) -> dict[str, str]:
    """Say hiya as a user."""

    return {"greeting": f"Hiya, {current_user.email}! &:D"}
