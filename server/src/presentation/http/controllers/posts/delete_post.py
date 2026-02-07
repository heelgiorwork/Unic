from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from src.core.exceptions.base import DomainTypeError
from src.core.exceptions.post import PostNotFoundError
from src.infrastructure.auth.exceptions import AuthenticationError
from src.infrastructure.exceptions.gateway import DataMapperError
from src.presentation.http.auth.openapi_marker import cookie_scheme
from src.presentation.http.errors.callbacks import log_error, log_info
from src.presentation.http.errors.translators import ServiceUnavailableTranslator
from src.services.commands.delete_post import (
    DeletePostInteractor,
    DeletePostRequest,
)
from src.services.common.exceptions.authorization import AuthorizationError


def create_delete_post_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{post_id}",
        description=getdoc(DeletePostInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            PostNotFoundError: status.HTTP_404_NOT_FOUND,
            DataMapperError: rule(
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
    async def delete_post(
        post_id: UUID,
        interactor: FromDishka[DeletePostInteractor],
    ) -> None:
        request_data = DeletePostRequest(post_id=post_id)
        await interactor.execute(request_data)
        return None

    return router
