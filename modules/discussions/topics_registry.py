"""TODO."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions import PiazzaException
from modules.discussions.models import DiscussionTopic


class TopicsRegistry:
    """TODO."""

    __PIAZZA_TOPICS = ["Politics", "Health", "Sport", "Tech"]

    __piazza_db_topic_ids: dict[str, int] = {}

    @classmethod
    def seed_piazza_db(cls, db: Session) -> None:
        """TODO."""

        try:
            statement = select(DiscussionTopic)
            for row in db.execute(statement):
                topic = row[0]
                # pyrefly: ignore
                cls.__piazza_db_topic_ids[topic.name] = topic.id

            for topic in cls.__PIAZZA_TOPICS:
                if topic not in cls.__piazza_db_topic_ids:
                    db_topic = DiscussionTopic(name=topic)
                    db.add(db_topic)
                    db.commit()
                    db.refresh(db_topic)
                    # pyrefly: ignore
                    cls.__piazza_db_topic_ids[topic] = db_topic.id

        except SQLAlchemyError as err:
            raise PiazzaException(
                "Failed to seed discussion topics: " + str(err)
            )

    @classmethod
    def get_piazza_db_id(cls, topic: str) -> Optional[int]:
        """TODO."""
        return cls.__piazza_db_topic_ids.get(topic)
