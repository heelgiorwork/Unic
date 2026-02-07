from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from src.core.exceptions.post import PostNotFoundError
from src.infrastructure.auth.exceptions import AuthenticationError
from src.infrastructure.exceptions.gateway import DataMapperError, ReaderError
from src.presentation.http.auth.openapi_marker import cookie_scheme
from src.presentation.http.errors.callbacks import log_error, log_info
from src.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)
from src.services.commands.get_post import (
    GetPostByIdInteractor,
    GetPostByIdRequest,
    GetPostByIdResponse,
)


def create_get_post_by_id_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{post_id}",
        description=getdoc(GetPostByIdInteractor),
        response_model=GetPostByIdResponse,
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            PostNotFoundError: status.HTTP_404_NOT_FOUND,
            ReaderError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def get_post_by_id(
        post_id: UUID,
        interactor: FromDishka[GetPostByIdInteractor],
    ) -> GetPostByIdResponse:
        result = await interactor.execute(GetPostByIdRequest(post_id=post_id))

        return GetPostByIdResponse(
            id=result.id,
            author_id=result.author_id,
            title=result.title,
            content=result.content,
            status=result.status,
            created_at=result.created_at,
        )

    return router
