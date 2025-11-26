from dishka import Provider

from .database import DatabaseProvider
from .services import ServiceProvider
from .uow import UowProvider


def get_providers() -> list[Provider]:
    return [
        DatabaseProvider(),
        UowProvider(),
        ServiceProvider(),
    ]
