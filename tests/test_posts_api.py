import datetime
import uuid
from typing import Any

import pytest
from elasticsearch import NotFoundError
from httpx import AsyncClient

from src.infrastructure.db.postgres.schemas.post import Post as PostDB


@pytest.mark.anyio
async def test_search_posts_success(
    client: AsyncClient, db_repository: Any, elastic_repository: Any
) -> None:
    """Тест успешного поиска: создает пост, находит его через API и удаляет."""

    test_id = str(uuid.uuid4())
    unique_word = f"уникальноеслово_{uuid.uuid4().hex[:6]}"
    test_text = f"Это пост, в котором есть {unique_word} для проверки поиска."

    new_db_post = PostDB(
        id=uuid.UUID(test_id),
        text=test_text,
        created_date=datetime.datetime.now(),
        rubrics=[],
    )
    db_repository.session.add(new_db_post)
    await db_repository.session.commit()

    async with elastic_repository._elastic_connection as es_client:
        await es_client.index(
            index=elastic_repository._index_name,
            id=test_id,
            document={"id": test_id, "text": test_text},
        )
        await es_client.indices.refresh(index=elastic_repository._index_name)

    try:
        response = await client.get("/posts/", params={"query": unique_word})

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "API вернул пустой список, хотя пост должен был найтись!"

        found_post_ids = [post["id"] for post in data]
        assert test_id in found_post_ids, (
            f"ID созданного поста {test_id} отсутствует в результатах поиска!"
        )

    finally:
        post_in_db = await db_repository.session.get(PostDB, test_id)
        if post_in_db:
            await db_repository.session.delete(post_in_db)
            await db_repository.session.commit()

        async with elastic_repository._elastic_connection as es_client:
            try:
                await es_client.delete(index=elastic_repository._index_name, id=test_id)
                await es_client.indices.refresh(index=elastic_repository._index_name)
            except NotFoundError:
                pass


@pytest.mark.anyio
async def test_search_posts_not_found(client: AsyncClient) -> None:
    impossible_query = f"абсурдный_запрос_{uuid.uuid4().hex}"
    response = await client.get("/posts/", params={"query": impossible_query})

    assert response.status_code == 404
    data = response.json()
    assert data["message"] == "Пост не найден"
    assert data["errors"][0]["type"] == "NOT_FOUND_ERROR"


@pytest.mark.anyio
async def test_search_posts_validation_error(client: AsyncClient) -> None:
    response = await client.get("/posts/")

    assert response.status_code == 422
    data = response.json()
    assert data["message"] == "Произошла ошибка проверки"
    assert data["errors"][0]["type"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_delete_post_success(
    client: AsyncClient, session: Any, elastic_repository: Any
) -> None:
    """Тест успешного каскадного удаления существующего поста через API."""

    test_id = str(uuid.uuid4())
    test_text = "Этот пост будет удален в тесте удаления"

    new_db_post = PostDB(
        id=uuid.UUID(test_id),
        text=test_text,
        created_date=datetime.datetime.now(),
        rubrics=[],
    )

    session.add(new_db_post)
    await session.commit()

    async with elastic_repository._elastic_connection as es_client:
        await es_client.index(
            index=elastic_repository._index_name,
            id=test_id,
            document={"id": test_id, "text": test_text},
        )
        await es_client.indices.refresh(index=elastic_repository._index_name)

    response = await client.delete(f"/posts/{test_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "post deleted"}

    async with elastic_repository._elastic_connection as es_client:
        with pytest.raises(NotFoundError):
            await es_client.get(index=elastic_repository._index_name, id=test_id)


@pytest.mark.anyio
async def test_delete_post_not_found(client: AsyncClient) -> None:
    """Тест удаления несуществующего поста."""
    fake_id = str(uuid.uuid4())

    response = await client.delete(f"/posts/{fake_id}")

    assert response.status_code == 404
