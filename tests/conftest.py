import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

# Hardcode a secret before we import any of the Pizza codes.
os.environ["JWT_SECRET"] = "0123456789ABCDEF0123456789ABCDEF"

from application import create_app
from database import create_sqlite_engine, get_db
from modules.discussions.topics_registry import TopicsRegistry
from modules.discussions.utils import get_current_time


@pytest.fixture
def session_frobbers():
    """Use this fixture to configure the SQLAlchemy Sessions implied by users
    of the client fixture."""

    return []


# @pytest.fixture
def fake_time():
    """TODO."""

    return datetime.strptime("2026-11-24T22:47:30Z", "%Y-%m-%dT%H:%M:%S%z")


@pytest.fixture
def client(tmp_path, session_frobbers):
    """Use this fixture for FastAPI integration tests that use a temporary,
    throwaway, database."""

    engine = create_sqlite_engine(tmp_path / "piazza-test.db")
    sessions = sessionmaker(bind=engine)

    TopicsRegistry._reset()
    app = create_app(engine)

    def override_db():
        with sessions() as session:
            for frob in session_frobbers:
                frob(session)
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_time] = fake_time
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
