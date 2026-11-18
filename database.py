"""Piazza's SQLAlchemy-based database layer."""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_PATH = os.environ.get(
    "DATABASE_PATH", Path(__file__).resolve().parent / "piazza.db"
)


def create_sqlite_engine(database_file: Path) -> Engine:
    """Create an SQLite-based SQLAlchemy engine."""

    database_url = f"sqlite:///{database_file}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )

    # fmt: off
    # ruff: disable[E501]

    # Source - https://stackoverflow.com/a/67228228
    # Posted by xjcl, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-11-16, License - CC BY-SA 4.0

    event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))

    # ruff: enable[E501]
    # fmt: on

    return engine


engine = create_sqlite_engine(Path(DATABASE_PATH))


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session]:
    """Get an SQLAlchemy database Session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
