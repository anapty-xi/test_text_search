import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.post import Post
from src.infrastructure.db.postgres.schemas.post import Post as PostDB

logger = logging.getLogger(__name__)


class PostRepository:
    """
    Репозиторий для управления сущностями постов в базе данных Postgres.

    Предоставляет методы для чтения и удаления записей с использованием асинхронной сессии SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_posts_by_ids(self, ids: list[str]) -> list[Post]:
        """
        Выгружает список постов из БД по их уникальным идентификаторам.

        Принимает список строковых ID, конвертирует их в объекты UUID, выполняет
        SQL-запрос выборки (SELECT IN) и сортирует результат по дате создания в обратном порядке.
        """
        logger.info(f"Database query: Fetching posts for {len(ids)} string IDs.")

        uuid_ids = [uuid.UUID(post_id) for post_id in ids]
        posts = await self.session.execute(
            select(PostDB)
            .filter(PostDB.id.in_(uuid_ids))
            .order_by(PostDB.created_date.desc())
        )
        db_posts = posts.scalars().all()
        logger.info(
            f"Database response: Found {len(db_posts)} rows in Postgres matching criteria."
        )

        validated_posts = [Post.model_validate(post) for post in db_posts]
        logger.debug(
            f"Successfully validated {len(validated_posts)} posts into core domain models."
        )

        return validated_posts

    async def delete_post(self, post_id: str) -> bool:
        """
        Удаляет пост из базы данных по его ID, если он существует.

        Ищет запись в Postgres по первичному ключу. Если запись найдена, удаляет её
        из текущей сессии. Метод возвращает статус успешности операции.
        """
        logger.info(
            f"Database query: Attempting to find post for deletion with id: {post_id}"
        )

        post = await self.session.get(PostDB, post_id)
        if post:
            logger.info(
                f"Post {post_id} found in Postgres. Mark for deletion from session."
            )
            await self.session.delete(post)
            logger.info(f"Post {post_id} successfully registered for deletion.")
            return True
        logger.warning(f"Post {post_id} not found in database. Nothing to delete.")
        return False
