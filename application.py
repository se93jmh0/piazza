"""The Pizza Application."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create the Piazza FastAPI application."""

    app = FastAPI()

    @app.get("/")
    def home() -> dict[str, str]:
        return {"greeting": "Welcome to Piazza!"}

    return app
