from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.export import router as export_router
from app.api.generate import router as generate_router
from app.api.health import router as health_router
from app.api.history import router as history_router
from app.logging.config import configure_logging
from app.logging.middleware import RequestIDMiddleware
from app.storage.database import create_tables


def create_app() -> FastAPI:
    configure_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        create_tables()
        yield

    app = FastAPI(title="MVP Generator", version="0.2.0", lifespan=lifespan)

    app.add_middleware(RequestIDMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(generate_router, prefix="/generate", tags=["generate"])
    app.include_router(history_router, prefix="/history", tags=["history"])
    app.include_router(export_router, prefix="/export", tags=["export"])

    return app


app = create_app()
