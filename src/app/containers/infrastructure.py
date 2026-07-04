from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    ContextLocalResource,
    Factory,
    Resource,
)

from src.infrastructure.db.elastic.engine import (
    ElasticConnectionsHandler,
    ElasticContext,
    init_elastic_client,
)
from src.infrastructure.db.elastic.gateways.posts import ElasticSearchRepository
from src.infrastructure.db.postgres.engine import (
    DbConnectionsHandler,
    SessionContext,
    init_db_engine,
)
from src.infrastructure.db.postgres.gateways.posts import PostRepository


class InfrastructureContainer(DeclarativeContainer):
    config = Configuration()

    db: Resource[DbConnectionsHandler] = Resource(
        init_db_engine,
        db_url=config.provided.POSTGRES.URL,
    )

    db_connection = ContextLocalResource(
        SessionContext, session_factory=db.provided.session_factory
    )

    elastic: Resource[ElasticConnectionsHandler] = Resource(
        init_elastic_client,
        hosts=config.provided.ELASTIC.CLIENT,
        db_session_factory=db.provided.session_factory,
    )

    elastic_connection = ContextLocalResource(
        ElasticContext,
        client=elastic.provided.client,
        index_name=config.provided.ELASTIC.INDEX_NAME,
    )

    post_repository = Factory(
        PostRepository,
        session=db_connection,
    )

    search_repository = Factory(
        ElasticSearchRepository,
        elastic_connection=elastic_connection,
        index_name=config.provided.ELASTIC.INDEX_NAME,
    )
