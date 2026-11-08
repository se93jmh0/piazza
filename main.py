"""Definition of the Piazza ASGI application."""

from fastapi import FastAPI

from application import create_app

app: FastAPI = create_app(None)
