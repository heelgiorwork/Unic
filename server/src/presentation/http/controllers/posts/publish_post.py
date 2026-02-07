from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from src.core.exceptions.base import DomainTypeError
from src.core.exceptions.post import (
    PostNotFoundError,
    PostPublishNotPermittedError,
)
from src.infrastructure.auth.exceptions import AuthenticationError
from src.infrastructure.exceptions.gateway import DataMapperError
from src.presentation.http.auth.openapi_marker import cookie_scheme
from src.presentation.http.errors.callbacks import log_error, log_info
from src.presentation.http.errors.translators import ServiceUnavailableTranslator
from src.services.commands.publish_post import (
    PublishPostInteractor,
    PublishPostRequest,
)
from src.services.common.exceptions.authorization import AuthorizationError


def create_publish_post_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/{post_id}/publish",
        description=getdoc(PublishPostInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            PostNotFoundError: status.HTTP_404_NOT_FOUND,
            PostPublishNotPermittedError: status.HTTP_409_CONFLICT,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
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
    async def publish_post(
        post_id: UUID,
        interactor: FromDishka[PublishPostInteractor],
    ) -> None:
        request = PublishPostRequest(post_id=post_id)
        await interactor.execute(request)
        return None

    return router
