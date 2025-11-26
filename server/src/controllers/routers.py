from fastapi import APIRouter

from .user import router


def get_routers() -> list[APIRouter]:
    return [
        router,
    ]
