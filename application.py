"""The Piazza Application."""

from fastapi import FastAPI
from sqlalchemy import Engine

import models
from database import engine
from routers import auth


def create_app(db_engine: Engine = engine) -> FastAPI:
    """Create the Piazza FastAPI application."""

    models.Base.metadata.create_all(bind=db_engine)

    app = FastAPI()
    app.include_router(auth.router, prefix="/auth")

    @app.get("/")
    def home() -> dict[str, str]:
        return {"greeting": "Welcome to Piazza!"}

    return app
