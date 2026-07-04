import logging
from collections.abc import AsyncGenerator
from types import TracebackType

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_bulk
from sqlalchemy import select

from src.core.config import config
from src.infrastructure.db.postgres.engine import SessionContext

logger = logging.getLogger(__name__)


class ElasticConnectionsHandler:
    """Управление подключением к Elasticsearch."""

    def __init__(self, hosts: str) -> None:
        self._hosts = hosts
        self.client = AsyncElasticsearch(hosts=self._hosts)

    async def client_close(self) -> None:
        if self.client:
            await self.client.close()


class ElasticContext:
    """Аналог SessionContext для Elasticsearch.

    Предоставляет клиент для работы и гарантирует обновление индекса (refresh)
    при успешном завершении операции.
    """

    def __init__(self, client: AsyncElasticsearch, index_name: str = "posts") -> None:
        self._client = client
        self._index_name = index_name

    async def __aenter__(self) -> AsyncElasticsearch:
        return self._client

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass


async def _create_index_and_import_from_db(
    client: AsyncElasticsearch, db_session_factory: SessionContext
) -> None:
    """Проверяет индекс Эластика. Если его нет — создает и наполняет данными из Postgres."""

    from src.infrastructure.db.postgres.schemas.post import Post

    index = config.ELASTIC.INDEX_NAME
    try:
        try:
            exists = await client.indices.exists(index=index)
        except Exception as head_err:
            logger.warning(f"HEAD request failed, trying alternative check: {head_err}")
            try:
                await client.indices.get(index=index)
                exists = True
            except NotFoundError:
                exists = False

        if exists:
            logger.info(f"Индекс '{index}' уже существует. Пропускаем импорт из БД.")
            return

        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "text": {
                        "type": "text",
                        "analyzer": "russian",
                    },
                }
            }
        }
        await client.indices.create(index=index, body=mapping)
        logger.info(f"Index '{index}' created")

        logger.info("Reading Postgres for Elastic index initialization...")
        async with SessionContext(db_session_factory) as session:
            query = select(Post.id, Post.text)
            result = await session.execute(query)
            posts = result.all()

        actions = []
        for post in posts:
            str_uuid = str(post.id)
            action = {
                "_index": index,
                "_id": str_uuid,
                "_source": {"id": str_uuid, "text": post.text},
            }
            actions.append(action)

        if actions:
            success, errors = await async_bulk(client, actions)
            logger.info(
                f"Imported {success} records into Elasticsearch with fresh IDs. Errors: {len(errors)}"
            )

            await client.indices.refresh(index=index)
        else:
            logger.warning(
                "Postgres table is empty. Nothing to index in Elasticsearch."
            )

    except Exception as e:
        logger.error(
            f"Error during Elasticsearch data initialization: {e}", exc_info=True
        )


async def init_elastic_client(
    hosts: str, db_session_factory: SessionContext
) -> AsyncGenerator[ElasticConnectionsHandler]:
    elastic_handler = ElasticConnectionsHandler(hosts=hosts)
    await _create_index_and_import_from_db(elastic_handler.client, db_session_factory)
    yield elastic_handler
    await elastic_handler.client_close()
