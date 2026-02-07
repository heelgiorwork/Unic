from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict

from src.core.exceptions.base import DomainTypeError
from src.core.exceptions.post import (
    PostEditNotPermittedError,
)
from src.infrastructure.auth.exceptions import AuthenticationError
from src.infrastructure.exceptions.gateway import DataMapperError
from src.presentation.http.auth.openapi_marker import cookie_scheme
from src.presentation.http.errors.callbacks import log_error, log_info
from src.presentation.http.errors.translators import ServiceUnavailableTranslator
from src.services.commands.create_post import (
    CreatePostInteractor,
    CreatePostRequest,
    CreatePostResponse,
)
from src.services.common.exceptions.authorization import AuthorizationError


class CreatePostRequestPydantic(BaseModel):
    """
    Pydantic используется только для OpenAPI.
    """

    model_config = ConfigDict(frozen=True)

    title: str
    content: str


def create_create_post_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        description=getdoc(CreatePostInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            PostEditNotPermittedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def create_post(
        request_data_pydantic: CreatePostRequestPydantic,
        interactor: FromDishka[CreatePostInteractor],
    ) -> CreatePostResponse:
        request_data = CreatePostRequest(
            title=request_data_pydantic.title,
            content=request_data_pydantic.content,
        )
        return await interactor.execute(request_data)

    return router
