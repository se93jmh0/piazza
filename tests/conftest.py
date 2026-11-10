import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# Hardcode a secret before we import any of the Pizza codes.
os.environ["JWT_SECRET"] = "0123456789ABCDEF0123456789ABCDEF"

from application import create_app
from database import get_db


@pytest.fixture
def session_frobbers():
    """Use this fixture to configure the SQLAlchemy Sessions implied by users
    of the client fixture."""

    return []


@pytest.fixture
def client(tmp_path, session_frobbers):
    """Use this fixture for FastAPI integration tests that use a temporary,
    throwaway, database."""

    engine = create_engine(
        f"sqlite:///{tmp_path / 'piazzza-test.db'}",
        connect_args={"check_same_thread": False},
    )
    sessions = sessionmaker(bind=engine)
    app = create_app(engine)

    def override_db():
        with sessions() as session:
            for frob in session_frobbers:
                frob(session)
            yield session

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
