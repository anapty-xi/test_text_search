import csv
import logging
import os
from collections.abc import AsyncGenerator
from datetime import datetime
from types import TracebackType

from sqlalchemy import func, select
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


async def _load_csv_to_postgres_if_empty(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Проверяет, пуста ли таблица в Postgres. Если да — заливает CSV."""
    from src.infrastructure.db.postgres.schemas.post import Post

    CSV_FILE_PATH = "posts.csv"
    if not os.path.exists(CSV_FILE_PATH):
        logger.warning(
            f"File {CSV_FILE_PATH} not found. Skipping Postgres initialization."
        )
        return

    async with SessionContext(session_factory) as session:
        count_query = select(func.count()).select_from(Post)
        result = await session.execute(count_query)
        count = result.scalar() or 0

        if count > 0:
            logger.info("In Postgres there are already data. Skipping CSV import.")
            return

        logger.info("Postgres is empty. Starting CSV import...")

        documents_to_insert = []
        with open(CSV_FILE_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rubrics_list = (
                    [r.strip() for r in row["rubrics"].strip("[]'\"").split(",")]
                    if "rubrics" in row
                    else []
                )

                created_date = datetime.now()
                if "created_date" in row:
                    try:
                        created_date = datetime.fromisoformat(row["created_date"])
                    except ValueError:
                        pass

                doc = Post(
                    text=row.get("text", ""),
                    rubrics=rubrics_list,
                    created_date=created_date,
                )
                documents_to_insert.append(doc)

        if documents_to_insert:
            session.add_all(documents_to_insert)
            await session.flush()
            logger.info(
                f"Successfully added {len(documents_to_insert)} records to Postgres."
            )


async def init_db_engine(db_url: str) -> AsyncGenerator[DbConnectionsHandler]:
    db_engine = DbConnectionsHandler(db_url=db_url)
    await _load_csv_to_postgres_if_empty(db_engine.session_factory)
    yield db_engine
    await db_engine.engine_close()
