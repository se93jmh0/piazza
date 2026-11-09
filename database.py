"""TODO."""

from pathlib import Path
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.session import Session

Base = declarative_base()


class Database:
    """."""

    def __init__(self, db_path: Path) -> None:
        """."""
        DATABASE_URL = f"sqlite:///{db_path}"
        self.engine = create_engine(
            DATABASE_URL, connect_args={"check_same_thread": False}
        )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

