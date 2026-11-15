"""The Piazza Application."""

from fastapi import FastAPI
from sqlalchemy import Engine
from sqlalchemy.orm import Session

import models
import modules.discussions.routes
from database import engine
from modules.discussions.topics_registry import TopicsRegistry
from routers import auth


def create_app(db_engine: Engine = engine) -> FastAPI:
    """Create the Piazza FastAPI application."""

    models.Base.metadata.create_all(bind=db_engine)
    with Session(db_engine) as session:
        TopicsRegistry.seed_piazza_db(session)

    app = FastAPI()
    app.include_router(auth.router, prefix="/auth")
    app.include_router(modules.discussions.routes.router)

    @app.get("/")
    def home() -> dict[str, str]:
        return {"greeting": "Welcome to Piazza!"}

    return app
