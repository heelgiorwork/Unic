from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from src.core.exceptions.base import DomainTypeError
from src.infrastructure.auth.exceptions import (
    AuthenticationChangeError,
    AuthenticationError,
    ReAuthenticationError,
)
from src.infrastructure.auth.handlers.change_password import (
    ChangePasswordHandler,
    ChangePasswordRequest,
)
from src.infrastructure.exceptions.gateway import DataMapperError
from src.infrastructure.exceptions.password_hasher import PasswordHasherBusyError
from src.presentation.http.auth.openapi_marker import cookie_scheme
from src.presentation.http.errors.callbacks import log_error, log_info
from src.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)
from src.services.common.exceptions.authorization import AuthorizationError


def create_change_password_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/password",
        description=getdoc(ChangePasswordHandler),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            AuthenticationChangeError: status.HTTP_400_BAD_REQUEST,
            ReAuthenticationError: status.HTTP_403_FORBIDDEN,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def change_password(
        current_password: Annotated[str, Body()],
        new_password: Annotated[str, Body()],
        handler: FromDishka[ChangePasswordHandler],
    ) -> None:
        request_data = ChangePasswordRequest(
            current_password=current_password,
            new_password=new_password,
        )
        await handler.execute(request_data)

    return router
