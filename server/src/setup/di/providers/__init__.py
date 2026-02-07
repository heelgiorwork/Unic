from dishka import Provider

from .auth import AuthProvider
from .auth_handlers import AuthHandlersProvider
from .core import CoreProvider
from .database import DatabaseProvider
from .services import ApplicationProvider
from .uow import UowProvider


def get_providers() -> list[Provider]:
    return [
        DatabaseProvider(),
        UowProvider(),
        AuthProvider(),
        AuthHandlersProvider(),
        ApplicationProvider(),
        CoreProvider(),
    ]
