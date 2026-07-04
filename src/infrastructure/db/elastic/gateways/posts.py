import asyncio
import logging

from elasticsearch import NotFoundError

from src.infrastructure.db.elastic.engine import ElasticContext

logger = logging.getLogger(__name__)


class ElasticSearchRepository:
    def __init__(
        self,
        elastic_connection: ElasticContext,
        index_name: str,
    ) -> None:
        self._elastic_connection = elastic_connection
        self._index_name = index_name

    async def search(self, query: str) -> list[str]:
        """Ищет документы по совпадению текста и возвращает список строковых ID."""

        async with self._elastic_connection as es_client:
            response = await es_client.search(
                index=self._index_name,
                query={"match": {"text": {"query": query, "operator": "and"}}},
                size=20,
            )

            hits = response["hits"]["hits"]
            logger.info(
                f"Found {len(hits)} hits for query '{query}' in index '{self._index_name}'"
            )
            return [hit["_id"] for hit in hits]

    async def delete_post(self, post_id: str) -> None:
        """Удаляет документ из поискового индекса по ID."""

        async with self._elastic_connection as es_client:
            try:
                await es_client.delete(
                    index=self._index_name,
                    id=post_id,
                )
            except NotFoundError:
                logger.warning(
                    f"Post with id {post_id} not found in Elastic index, skipping delete"
                )
            try:
                await asyncio.shield(
                    es_client.indices.refresh(
                        index=self._index_name, ignore_unavailable=True
                    )
                )
            except Exception as e:
                logger.error(f"Failed to refresh Elastic index after deletion: {e}")
