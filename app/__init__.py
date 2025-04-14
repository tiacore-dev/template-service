from fastapi import FastAPI
from app.routes import register_routes


def create_app() -> FastAPI:
    app = FastAPI()

    register_routes(app)

    return app
