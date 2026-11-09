"""."""

from typing import Any, Generator

from sqlalchemy.orm.session import Session

from database import Database


class Runtime:
    """."""

    __me: Runtime

    def __init__(self, database: Database) -> None:
        """."""
        self.database = database
        Runtime.__me = self

    @staticmethod
    def get() -> Runtime:
        """."""
        return Runtime.__me

    def get_db_session(self) -> Generator[Session, Any]:
        """TODO."""

        # Open one database session for the request.
        db = self.database.SessionLocal()
        try:
            yield db
        finally:
            # Close it after the request finishes.
            db.close()
