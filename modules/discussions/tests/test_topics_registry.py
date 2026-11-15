from unittest.mock import DEFAULT, Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import database
from exceptions import PiazzaProblem
from modules.discussions.models import DiscussionTopic
from modules.discussions.topics_registry import TopicsRegistry


@pytest.fixture
def test_db(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'piazza-test.db'}")
    database.Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.mark.parametrize("topic", ["Politics", "Health", "Sport", "Tech"])
def test_get_db_id(test_db, topic):
    TopicsRegistry.init(test_db)

    id = TopicsRegistry.get_db_id(topic)

    assert id is not None
    assert id > 0


def test_get_db_id_unknown_topic(test_db):
    TopicsRegistry.init(test_db)

    id = TopicsRegistry.get_db_id("foo")

    assert id is None


def test_init_is_database_idempotent(test_db):
    TopicsRegistry._reset()
    test_db.execute = Mock(wraps=test_db.execute)
    test_db.add = Mock(wraps=test_db.add)
    TopicsRegistry.init(test_db)
    assert test_db.execute.call_count > 0
    # ["Politics", "Health", "Sport", "Tech"]
    assert test_db.add.call_count == 4

    TopicsRegistry._reset()
    test_db.execute.reset_mock()
    test_db.add.reset_mock()
    TopicsRegistry.init(test_db)

    test_db.execute.assert_called()
    test_db.add.assert_not_called()


def test_init_encounters_SQLAlchemyError(test_db):
    TopicsRegistry._reset()
    already_injected = False

    def inject_Tech_topic(*args, **kwargs):
        nonlocal already_injected
        if not already_injected:
            already_injected = True
            db_topic = DiscussionTopic(name="Tech")
            test_db.add(db_topic)
            test_db.commit()

        return DEFAULT

    test_db.add = Mock(wraps=test_db.add, side_effect=inject_Tech_topic)

    with pytest.raises(PiazzaProblem) as err:
        TopicsRegistry.init(test_db)

    assert "topic" in str(err)
