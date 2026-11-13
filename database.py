"""Piazza's SQLAlchemy-based database layer."""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_PATH = os.environ.get(
    "DATABASE_PATH", Path(__file__).resolve().parent / "piazza.db"
)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session]:
    """Get an SQLAlchemy database Session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
