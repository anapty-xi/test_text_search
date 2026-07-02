from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    ContextLocalResource,
    Resource,
)

from src.infrastructure.db.elastic.engine import (
    ElasticConnectionsHandler,
    ElasticContext,
    init_elastic_client,
)
from src.infrastructure.db.postgres.engine import (
    DbConnectionsHandler,
    SessionContext,
    init_db_engine,
)


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
        elastic_url=config.provided.ELASTIC.URL,
    )

    elastic_connection = ContextLocalResource(
        ElasticContext,
        client=elastic.provided.ELASTIC.CLIENT,
        index_name=config.provided.ELASTIC.INDEX_NAME,
    )
