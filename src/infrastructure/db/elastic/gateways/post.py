from typing import AsyncContextManager, Callable

from elasticsearch import AsyncElasticsearch


class ElasticSearchRepository:
    def __init__(
        self,
        elastic_connection: Callable[[], AsyncContextManager[AsyncElasticsearch]],
        index_name: str,
    ) -> None:
        """Репозиторий принимает фабрику контекста Эластика и имя индекса."""
        self._elastic_connection = elastic_connection
        self._index_name = index_name

    async def search(self, query: str) -> list[str]:
        """Ищет документы по совпадению текста и возвращает список строковых ID."""
        async with self._elastic_connection() as es_client:
            response = await es_client.search(
                index=self._index_name,
                query={"match": {"text": query}},
                size=20,
            )

            hits = response["hits"]["hits"]
            return [hit["_id"] for hit in hits]

    async def delete_post(self, post_id: str) -> None:
        """Удаляет документ из поискового индекса по ID."""

        async with self._elastic_connection() as es_client:
            await es_client.delete(index=self._index_name, id=post_id)
