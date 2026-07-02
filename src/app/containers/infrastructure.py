from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    ContextLocalResource,
    Resource,
)

from src.infrastructure.db.engine import (
    DbConnectionsHandler,
    SessionContext,
    init_db_engine,
)


class InfrastructureContainer(DeclarativeContainer):
    config = Configuration()

    db: Resource[DbConnectionsHandler] = Resource(
        init_db_engine,
        db_url=config.provided.POSTGRES.DB_URL,
    )

    db_connection = ContextLocalResource(
        SessionContext, session_factory=db.provided.session_factory
    )
