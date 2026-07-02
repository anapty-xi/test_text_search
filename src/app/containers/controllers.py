from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    DependenciesContainer,
)


class ControllersContainer(DeclarativeContainer):
    infrastructure = DependenciesContainer()
