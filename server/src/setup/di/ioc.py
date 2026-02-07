from dishka import AsyncContainer, make_async_container

from src.setup.config import AppConfig

from .providers import get_providers


def create_container(config: AppConfig) -> AsyncContainer:
    context = {AppConfig: config}
    container = make_async_container(*get_providers(), context=context)
    return container
