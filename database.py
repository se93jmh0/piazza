"""TODO."""

from pathlib import Path
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.session import Session

import constants

DATABASE_URL = f"sqlite:///{constants.PIAZZA_DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, Any]:
    """TODO."""

    # Open one database session for the request.
    db = SessionLocal()
    try:
        yield db
    finally:
        # Close it after the request finishes.
        db.close()
