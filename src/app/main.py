from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.app.system.resources import (
    AppContainer,
    FastApiDi,
    shutdown_event,
    startup_event,
)
from src.core.config import config


@asynccontextmanager
async def lifespan(app: FastApiDi) -> AsyncGenerator[None, None]:
    await startup_event(app)
    yield
    await shutdown_event(app)


def create_app() -> FastApiDi:
    app = FastApiDi(lifespan=lifespan)
    container = AppContainer(config=config)
    app.container = container

    return app


app = create_app()
