"""Piazza's SQLAlchemy database models."""

from sqlalchemy import Column, Integer, String

from database import Base


class User(Base):
    """A Piazza user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
