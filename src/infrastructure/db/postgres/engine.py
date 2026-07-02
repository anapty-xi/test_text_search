import logging
from collections.abc import AsyncGenerator
from types import TracebackType

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    AsyncSessionTransaction,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


logger = logging.getLogger(__name__)


class DbConnectionsHandler:
    """Управление подключениями к базе данных."""

    def __init__(self, db_url: str) -> None:
        self._db_url = db_url
        self._engine: AsyncEngine | None = create_async_engine(self._db_url, echo=False)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self._engine, expire_on_commit=False
        )

    async def engine_close(self) -> None:
        """Закрывает движок и фабрику сессий."""

        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._async_session = None


class SessionContext:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._transaction_context: AsyncSessionTransaction | None = None

    async def __aenter__(self) -> AsyncSession:
        self._session = self._session_factory()
        self._transaction_context = self._session.begin()
        await self._transaction_context.__aenter__()
        return self._session

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        assert self._transaction_context is not None
        try:
            await self._transaction_context.__aexit__(exc_type, exc_val, exc_tb)
        finally:
            await self._session.close()


async def init_db_engine(db_url: str) -> AsyncGenerator[DbConnectionsHandler]:
    db_engine = DbConnectionsHandler(db_url=db_url)
    yield db_engine
    await db_engine.engine_close()
