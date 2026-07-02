from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Container
from fastapi import FastAPI

from src.app.containers.controllers import ControllersContainer
from src.app.containers.infrastructure import InfrastructureContainer


class FastApiDi(FastAPI):
    container: DeclarativeContainer


class AppContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(packages=["src.app.api"])
    config = Configuration(strict=True)

    infrastructure = Container(InfrastructureContainer, config=config.provided)

    controllers = Container(ControllersContainer, infrastructure=infrastructure)


async def startup_event(app: FastApiDi) -> None:
    """Инициализация ресурсов приложения"""
    await app.container.init_resources()  # type: ignore[misc]


async def shutdown_event(app: FastApiDi) -> None:
    """Закрытие ресурсов контейнера"""
    await app.container.shutdown_resources()  # type: ignore[misc]
