import logging
from collections.abc import AsyncGenerator
from types import TracebackType

from elasticsearch import AsyncElasticsearch

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
        if exc_type is None:
            try:
                await self._client.indices.refresh(
                    index=self._index_name, ignore_unavailable=True
                )
            except Exception as e:
                logger.error(f"Failed to refresh Elastic index: {e}")


async def init_elastic_client(hosts: str) -> AsyncGenerator[ElasticConnectionsHandler]:
    elastic_handler = ElasticConnectionsHandler(hosts=hosts)
    yield elastic_handler
    await elastic_handler.client_close()
