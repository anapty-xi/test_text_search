import logging

from src.core.entities.post import Post
from src.core.exceptions.posts import PostsNotFound
from src.core.usecases.posts.protocol import (
    RepositoryProtocol,
    SearchRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class Base:
    """Базовый класс для юзкейсов работы с постами.

    Обеспечивает доступом к репозиториям основного хранилища (Postgres)
    и поискового движка (Elasticsearch).
    """

    def __init__(
        self,
        repository: RepositoryProtocol,
        search_repository: SearchRepositoryProtocol,
    ) -> None:
        self.repository = repository
        self.search_repository = search_repository


class SearchPosts(Base):
    """
    Выполняет полнотекстовый поиск постов через Elasticsearch с последующей загрузкой из БД.

    Сначала запрашивает подходящие ID документов в Elasticsearch. Если ID найдены,
    выгружает полные объекты постов из Postgres.
    """

    async def execute(self, query: str) -> list[Post]:
        logger.info(f"Executing SearchPosts usecase for query: '{query}'")
        ids = await self.search_repository.search(query)
        if ids:
            logger.info(
                f"Elasticsearch found {len(ids)} matching document IDs for query '{query}'"
            )
            posts = await self.repository.get_posts_by_ids(ids)
            logger.info(
                f"Successfully retrieved {len(posts)} posts from database for query '{query}'"
            )
            return posts
        logger.warning(f"No posts matched the query '{query}' in Elasticsearch index.")
        raise PostsNotFound()


class DeletePost(Base):
    """
    Удаляет пост из базы данных Postgres и поискового индекса Elasticsearch.

    Сначала запись удаляется из реляционной базы данных. Если удаление прошло успешно
    (пост существовал), отправляется запрос на удаление документа из индекса Elastic.
    """

    async def execute(self, post_id: str) -> None:
        if await self.repository.delete_post(post_id):
            logger.info(
                f"Post {post_id} successfully deleted from Postgres. Proceeding to delete from Elasticsearch index..."
            )

            await self.search_repository.delete_post(post_id)
            logger.info(
                f"Post {post_id} successfully removed from Elasticsearch index."
            )
        else:
            logger.warning(
                f"Post {post_id} was not found in Postgres. Elasticsearch deletion skipped."
            )
