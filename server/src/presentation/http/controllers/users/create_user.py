from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from src.core.enums.user_role import UserRole
from src.core.exceptions.base import DomainTypeError
from src.core.exceptions.user import (
    RoleAssignmentNotPermittedError,
    UsernameAlreadyExistsError,
)
from src.infrastructure.auth.exceptions import AuthenticationError
from src.infrastructure.exceptions.gateway import DataMapperError
from src.infrastructure.exceptions.password_hasher import PasswordHasherBusyError
from src.presentation.http.auth.openapi_marker import cookie_scheme
from src.presentation.http.errors.callbacks import log_error, log_info
from src.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)
from src.services.commands.create_user import (
    CreateUserInteractor,
    CreateUserRequest,
    CreateUserResponse,
)
from src.services.common.exceptions.authorization import AuthorizationError


class CreateUserRequestPydantic(BaseModel):
    """
    Using a Pydantic model here is generally unnecessary.
    It's only implemented to render a specific Swagger UI (OpenAPI) schema.
    """

    model_config = ConfigDict(frozen=True)

    username: str
    password: str
    role: UserRole = Field(default=UserRole.USER)


def create_create_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        description=getdoc(CreateUserInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            RoleAssignmentNotPermittedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def create_user(
        request_data_pydantic: CreateUserRequestPydantic,
        interactor: FromDishka[CreateUserInteractor],
    ) -> CreateUserResponse:
        request_data = CreateUserRequest(
            username=request_data_pydantic.username,
            password=request_data_pydantic.password,
            role=request_data_pydantic.role,
        )
        return await interactor.execute(request_data)

    return router
