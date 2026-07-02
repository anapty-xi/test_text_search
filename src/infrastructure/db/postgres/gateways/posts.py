import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.post import Post
from src.infrastructure.db.postgres.schemas.post import Post as PostDB


class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_posts_by_ids(self, ids: list[str]) -> list[Post]:
        uuid_ids = [uuid.UUID(post_id) for post_id in ids]
        posts = await self.session.execute(
            select(PostDB)
            .filter(PostDB.id.in_(uuid_ids))
            .order_by(PostDB.created_date.desc())
        )
        return [Post.model_validate(post) for post in posts.scalars().all()]

    async def delete_post(self, post_id: str) -> bool:
        post = await self.session.get(PostDB, post_id)
        if post:
            await self.session.delete(post)
            return True
        return False
