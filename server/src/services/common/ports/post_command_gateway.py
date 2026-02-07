from abc import abstractmethod
from typing import Protocol, TypedDict
from uuid import UUID

from src.core.entities.post import Post
from src.core.enums.post_status import PostStatus
from src.core.value_objects.post_id import PostId
from src.core.value_objects.user_id import UserId
from src.services.common.query_params.offset_pagination import OffsetPaginationParams
from src.services.common.query_params.sorting import SortingParams


class PostQM(TypedDict):
    id_: UUID
    title: str
    author_id: UUID
    status: PostStatus


class ListPostsQM(TypedDict):
    posts: list[PostQM]
    total: int


class PostCommandGateway(Protocol):
    """Gateway for post reads used by command services and queries.

    - read_by_id: used by command services (via UnitOfWork)
    - read_all: query-style listing (pagination + sorting)
    - read_detail: query-style detailed view

    Mutating operations must be performed through UnitOfWork.
    """

    @abstractmethod
    async def read_by_id(
        self,
        post_id: PostId,
        for_update: bool = False,
    ) -> Post | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_all(
        self,
        *,
        author_id: UserId | None = None,
        status: PostStatus | None = None,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListPostsQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """
        ...
