from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.presentation.http.auth.asgi_middleware import ASGIAuthMiddleware
from src.presentation.http.controllers.root_router import create_root_router
from src.setup.config import AppConfig
from src.setup.di.providers import get_providers
from src.setup.lifespan import on_startup

config = AppConfig()
container = make_async_container(*get_providers(), context={AppConfig: config})


def get_app() -> FastAPI:
    fastapi_app = FastAPI()
    fastapi_app.add_middleware(ASGIAuthMiddleware)
    fastapi_app.include_router(create_root_router())
    setup_dishka(container, fastapi_app)

    @fastapi_app.on_event("startup")
    async def startup() -> None:
        await on_startup(container)

    return fastapi_app


app = get_app()
