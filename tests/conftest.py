from collections.abc import AsyncGenerator
from typing import Any, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.app.main import app
from src.infrastructure.db.postgres.gateways.posts import PostRepository


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def engine() -> AsyncEngine:
    infra_container = cast(Any, app.container).infrastructure
    db_handler = await infra_container.db()
    engine_instance = db_handler._engine
    return cast(AsyncEngine, engine_instance)


@pytest.fixture
async def session_factory(
    engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    connection = await engine.connect()
    transaction = await connection.begin()

    async_session = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        class_=AsyncSession,
        join_transaction_mode="create_savepoint",
    )

    yield async_session

    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as s:
        yield s


@pytest.fixture(autouse=True)
async def patch_repository_session(
    session: AsyncSession, elastic_repository: Any
) -> AsyncGenerator[None, None]:
    """Абсолютно безопасный патч репозитория.

    Подменяет сессию для изоляции в Postgres, но вообще не трогает
    и не очищает индекс Elasticsearch.
    """
    original_init = PostRepository.__init__

    def mock_init(self: PostRepository, *args: Any, **kwargs: Any) -> None:
        original_init(self, *args, **kwargs)
        self.session = session

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(PostRepository, "__init__", mock_init)

        # 🔥 Мы убрали весь блок es_client.indices.delete!
        # Теперь ваши боевые данные в Эластике в полной безопасности.
        yield


@pytest.fixture
async def db_repository(session: AsyncSession) -> PostRepository:
    return PostRepository(session=session)


@pytest.fixture
async def elastic_repository() -> Any:
    infra_container = cast(Any, app.container).infrastructure
    repo = await infra_container.search_repository()
    return repo
