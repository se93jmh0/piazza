"""."""

from fastapi import FastAPI
from sqlalchemy import Engine

import models
from database import engine
from routers import auth, profile


def create_app(db_engine: Engine = engine) -> FastAPI:
    """."""

    models.Base.metadata.create_all(bind=db_engine)
    app = FastAPI()
    app.include_router(auth.router, prefix="/auth")
    app.include_router(profile.router, prefix="/profile")

    @app.get("/")
    def home() -> dict[str, str]:
        return {"greeting": "Welcome to Piazza!"}

    return app
