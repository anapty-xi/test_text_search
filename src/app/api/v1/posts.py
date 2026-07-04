import logging
import uuid
from typing import Annotated

from dependency_injector.wiring import Closing, Provide, inject
from fastapi import APIRouter, Depends, Path, Query

from src.app.api.v1.dto import PostOut
from src.app.system.resources import AppContainer
from src.core.entities.post import Post
from src.core.usecases.posts.usecases import DeletePost, SearchPosts

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts")


@router.get(
    "/",
    response_model=list[PostOut],
    status_code=200,
    description="Retrieving 20 posts containing the submitted text query",
)
@inject
async def search_posts(
    query: Annotated[str, Query(description="Text query for post searching")],
    usecase: Annotated[
        SearchPosts, Depends(Closing[Provide[AppContainer.controllers.get_posts]])
    ],
) -> list[Post]:
    logger.info(f"Received GET request to search posts with query: '{query}'")
    res = await usecase.execute(query=query)
    logger.info(
        f"Successfully processed search query '{query}'. Returning {len(res)} posts."
    )
    return res


@router.delete(
    "/{post_id}",
    response_model=dict[str, str],
    status_code=200,
    description="Delete post by id",
)
@inject
async def delete_post(
    post_id: Annotated[uuid.UUID, Path(description="Post id")],
    usecase: Annotated[
        DeletePost, Depends(Closing[Provide[AppContainer.controllers.delete_post]])
    ],
) -> dict[str, str]:
    logger.info(f"Received DELETE request for post_id: {post_id}")
    await usecase.execute(post_id=post_id)
    logger.info(f"Successfully deleted post with id: {post_id}")
    return {"message": "post deleted"}
