from dishka import Provider, Scope, provide_all

from src.infrastructure.auth.handlers.change_password import ChangePasswordHandler
from src.infrastructure.auth.handlers.log_in import LogInHandler
from src.infrastructure.auth.handlers.log_out import LogOutHandler
from src.infrastructure.auth.handlers.sign_up import SignUpHandler


class AuthHandlersProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        SignUpHandler,
        LogInHandler,
        ChangePasswordHandler,
        LogOutHandler,
    )
