from dataclasses import dataclass

from src.core.enums.post_status import PostStatus
from src.core.value_objects.user_id import UserId
from src.services.common.ports.post_command_gateway import (
    ListPostsQM,
    PostCommandGateway,
)
from src.services.common.query_params.offset_pagination import OffsetPaginationParams
from src.services.common.query_params.sorting import SortingOrder, SortingParams


@dataclass(frozen=True, slots=True, kw_only=True)
class ListPostsRequest:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder
    author_id: UserId | None = None
    status: PostStatus | None = None


class ListPostsQueryService:
    """
    Сервис для получения списка постов (карточки).
    Публичный доступ — без авторизации.
    """

    def __init__(self, post_gateway: PostCommandGateway) -> None:
        self._post_gateway = post_gateway

    async def execute(self, request_data: ListPostsRequest) -> ListPostsQM:
        """
        :raises PaginationError:
        :raises SortingError:
        :raises ReaderError:
        """

        pagination = OffsetPaginationParams(
            limit=request_data.limit,
            offset=request_data.offset,
        )
        sorting = SortingParams(
            field=request_data.sorting_field,
            order=request_data.sorting_order,
        )

        response = await self._post_gateway.read_all(
            author_id=request_data.author_id,
            status=request_data.status,
            pagination=pagination,
            sorting=sorting,
        )

        return response
