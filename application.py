"""The Pizza Application."""

from typing import Any

from fastapi import FastAPI
from sqlalchemy.engine import Engine


def create_app(db_engine: Engine | None) -> FastAPI:
    """Create the Piazza FastAPI application."""

    app = FastAPI()

    @app.get("/")
    def home() -> dict[str, str]:
        return {"greeting": "Welcome to Piazza!"}

    return app
