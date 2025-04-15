from fastapi import FastAPI
from app.routes import register_routes
from logger import setup_logger


def create_app() -> FastAPI:
    setup_logger()
    app = FastAPI()

    register_routes(app)

    return app
