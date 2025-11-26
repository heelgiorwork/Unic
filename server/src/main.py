from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.controllers.routers import get_routers
from src.core.config import AppConfig
from src.infrastructure.di.providers import get_providers

config = AppConfig()
container = make_async_container(*get_providers(), context={AppConfig: config})


def get_app() -> FastAPI:
    fastapi_app = FastAPI()
    for router in get_routers():
        fastapi_app.include_router(router)
    setup_dishka(container, fastapi_app)
    return fastapi_app
