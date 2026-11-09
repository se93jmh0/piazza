"""The Piazza Application."""

from typing import Any

from fastapi import FastAPI
from sqlalchemy.engine import Engine

import constants
from auth import auth, models
from database import Database
from runtime import Runtime


def create_app(db_engine: Engine | None) -> FastAPI:
    """Create the Piazza FastAPI application."""

    database = Database(constants.PIAZZA_DATABASE_PATH)
    runtime = Runtime(database)

    models.Base.metadata.create_all(bind=database.engine)
    app = FastAPI()
    app.include_router(auth.router, prefix="/auth")

    @app.get("/")
    def home() -> dict[str, str]:
        return {"greeting": "Welcome to Piazza!"}

    return app
