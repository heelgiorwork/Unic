from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from src.core.enums.post_status import PostStatus
from src.core.value_objects.user_id import UserId
from src.infrastructure.auth.exceptions import AuthenticationError
from src.infrastructure.exceptions.gateway import DataMapperError, ReaderError
from src.presentation.http.auth.openapi_marker import cookie_scheme
from src.presentation.http.errors.callbacks import log_error, log_info
from src.presentation.http.errors.translators import ServiceUnavailableTranslator
from src.services.common.exceptions.query import PaginationError, SortingError
from src.services.common.ports.post_command_gateway import ListPostsQM
from src.services.common.query_params.sorting import SortingOrder
from src.services.queries.list_posts import ListPostsQueryService, ListPostsRequest


class ListPostsRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    limit: Annotated[int, Field(ge=1)] = 20
    offset: Annotated[int, Field(ge=0)] = 0
    sorting_field: Annotated[str, Field()] = "created_at"
    sorting_order: Annotated[SortingOrder, Field()] = SortingOrder.DESC

    author_id: UUID | None = None
    status: PostStatus | None = None


def create_list_posts_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/",
        description=getdoc(ListPostsQueryService),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            PaginationError: status.HTTP_400_BAD_REQUEST,
            SortingError: status.HTTP_400_BAD_REQUEST,
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
    async def list_posts(
        request_data_pydantic: Annotated[ListPostsRequestPydantic, Depends()],
        interactor: FromDishka[ListPostsQueryService],
    ) -> ListPostsQM:
        request_data = ListPostsRequest(
            limit=request_data_pydantic.limit,
            offset=request_data_pydantic.offset,
            sorting_field=request_data_pydantic.sorting_field,
            sorting_order=request_data_pydantic.sorting_order,
            author_id=(
                UserId(request_data_pydantic.author_id) if request_data_pydantic.author_id else None
            ),
            status=request_data_pydantic.status,
        )
        return await interactor.execute(request_data)

    return router
