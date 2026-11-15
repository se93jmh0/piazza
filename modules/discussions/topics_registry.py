"""The registry for Piazza discussion topics."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions import PiazzaProblem
from modules.discussions.models import DiscussionTopic


class TopicsRegistry:
    """The registry for Piazza discussion topics."""

    __PIAZZA_TOPIC_NAMES = ["Politics", "Health", "Sport", "Tech"]

    __db_ids: dict[str, int] = {}

    @staticmethod
    def _reset() -> None:
        """Forget all database IDs.  Mostly for unit tests."""

        TopicsRegistry.__db_ids = {}

    @classmethod
    def init(cls, db: Session) -> None:
        """Ensure that the Piazza database has all topic names."""

        try:
            for row in db.execute(select(DiscussionTopic)):
                topic = row[0]
                # pyrefly: ignore
                # Reason:
                #      Argument `InstrumentedAttribute[str]` is not assignable
                #      to parameter `key` with type `str` in function
                #      `dict.__setitem__`
                # Also applies to topic.id expression.
                cls.__db_ids[topic.name] = topic.id

            for topic in cls.__PIAZZA_TOPIC_NAMES:
                if topic not in cls.__db_ids:
                    db_topic = DiscussionTopic(name=topic)
                    db.add(db_topic)
                    db.commit()
                    # pyrefly: ignore
                    # Reason:
                    #     Argument `InstrumentedAttribute[int]` is not
                    #     assignable to parameter `value` with type `int` in
                    #     function `dict.__setitem__`
                    cls.__db_ids[topic] = db_topic.id

        except SQLAlchemyError as err:
            raise PiazzaProblem(
                "Failed to initialize discussion topics: " + str(err)
            )

    @classmethod
    def get_db_id(cls, topic: str) -> Optional[int]:
        """Get the ID of the specified topic in the database."""

        return cls.__db_ids.get(topic)
