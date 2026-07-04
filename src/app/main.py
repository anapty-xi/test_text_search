from contextlib import asynccontextmanager
from typing import AsyncGenerator

from elasticsearch import ApiError, TransportError
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DBAPIError

from src.app.api.v1.posts import router as posts_router
from src.app.system.resources import (
    AppContainer,
    FastApiDi,
    shutdown_event,
    startup_event,
)
from src.core.config import config
from src.core.exceptions.base import BaseAPIException
from src.core.exceptions.handlers.api_exception_handler import api_exception_handler
from src.core.exceptions.handlers.db_handler import db_error_handler
from src.core.exceptions.handlers.search_db_handler import search_db_error_handler
from src.core.exceptions.handlers.validation_handler import validation_exception_handler
from src.core.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastApiDi) -> AsyncGenerator[None, None]:
    await startup_event(app)
    yield
    await shutdown_event(app)


def create_app() -> FastApiDi:
    setup_logging()

    app = FastApiDi(lifespan=lifespan)
    container = AppContainer(config=config)
    app.container = container

    app.add_exception_handler(BaseAPIException, api_exception_handler)
    app.add_exception_handler(DBAPIError, db_error_handler)
    app.add_exception_handler(TransportError, search_db_error_handler)
    app.add_exception_handler(ApiError, search_db_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    app.include_router(posts_router)

    return app


app = create_app()
