from src.core.entities.post import Post
from src.core.exceptions.posts import PostsNotFound
from src.core.usecases.posts.protocol import (
    RepositoryProtocol,
    SearchRepositoryProtocol,
)


class Base:
    def __init__(
        self,
        repository: RepositoryProtocol,
        search_repository: SearchRepositoryProtocol,
    ) -> None:
        self.repository = repository
        self.search_repository = search_repository


class SearchPosts(Base):
    async def execute(self, query: str) -> list[Post]:
        ids = await self.search_repository.search(query)
        if ids:
            return await self.repository.get_posts_by_ids(ids)
        raise PostsNotFound()


class DeletePost(Base):
    async def execute(self, post_id: str) -> None:
        await self.repository.delete_post(post_id)
        await self.search_repository.delete_post(post_id)
