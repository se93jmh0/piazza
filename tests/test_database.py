from sqlalchemy.orm import Session

from database import get_db


def test_get_db():
    session = next(get_db())

    assert isinstance(session, Session)
