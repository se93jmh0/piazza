"""TODO."""

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions import PiazzaException
from modules.discussions.models import DiscussionTopic


class TopicsSeeder:
    """TODO."""

    __DEFAULT_TOPICS = ["Politics", "Health", "Sport", "Tech"]

    __db_topics = {}

    @staticmethod
    def init(db: Session) -> None:
        """TODO."""

        try:
            stmt = select(DiscussionTopic)
            for row in db.execute(stmt):
                topic = row[0]
                TopicsSeeder.__db_topics[topic.name] = topic.id

            for topic in TopicsSeeder.__DEFAULT_TOPICS:
                if topic not in TopicsSeeder.__db_topics:
                    db_topic = DiscussionTopic(name=topic)
                    db.add(db_topic)
                    db.commit()
                    db.refresh(db_topic)
                    TopicsSeeder.__db_topics[topic] = db_topic.id

        except SQLAlchemyError as err:
            raise PiazzaException(
                "Failed to seed discussion topics: " + str(err)
            )

    @staticmethod()