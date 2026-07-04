from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    DependenciesContainer,
    Factory,
)

from src.core.usecases.posts.usecases import DeletePost, SearchPosts


class ControllersContainer(DeclarativeContainer):
    infrastructure = DependenciesContainer()

    get_posts = Factory(
        SearchPosts,
        repository=infrastructure.post_repository,
        search_repository=infrastructure.search_repository,
    )

    delete_post = Factory(
        DeletePost,
        repository=infrastructure.post_repository,
        search_repository=infrastructure.search_repository,
    )
