from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from src.core.exceptions.base import DomainTypeError
from src.core.exceptions.user import (
    UserNotFoundByIdError,
)
from src.infrastructure.auth.exceptions import AuthenticationError
from src.infrastructure.exceptions.gateway import DataMapperError
from src.infrastructure.exceptions.password_hasher import PasswordHasherBusyError
from src.presentation.http.auth.openapi_marker import cookie_scheme
from src.presentation.http.errors.callbacks import log_error, log_info
from src.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)
from src.services.commands.set_user_password import (
    SetUserPasswordInteractor,
    SetUserPasswordRequest,
)
from src.services.common.exceptions.authorization import AuthorizationError


def create_set_user_password_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{user_id}/password",
        description=getdoc(SetUserPasswordInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundByIdError: status.HTTP_404_NOT_FOUND,
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
    async def set_user_password(
        user_id: Annotated[UUID, Path()],
        password: Annotated[str, Body()],
        interactor: FromDishka[SetUserPasswordInteractor],
    ) -> None:
        request_data = SetUserPasswordRequest(
            user_id=user_id,
            password=password,
        )
        await interactor.execute(request_data)

    return router
