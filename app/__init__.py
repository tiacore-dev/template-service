from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import register_routes
from logger import setup_logger


def create_app() -> FastAPI:
    setup_logger()
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_routes(app)

    return app
