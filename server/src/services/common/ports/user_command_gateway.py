from abc import abstractmethod
from typing import Protocol, TypedDict
from uuid import UUID

from src.core.entities.user import User
from src.core.enums.user_role import UserRole
from src.core.value_objects.user_id import UserId
from src.core.value_objects.username import Username
from src.services.common.query_params.offset_pagination import OffsetPaginationParams
from src.services.common.query_params.sorting import SortingParams


class UserQueryModel(TypedDict):
    id_: UUID
    username: str
    role: UserRole
    is_active: bool


class ListUsersQM(TypedDict):
    users: list[UserQueryModel]
    total: int


class UserCommandGateway(Protocol):
    """Gateway for user reads used by command services and queries.
    - Provides read_by_id / read_by_username (used by commands that need to
      lock/read entities for mutation via UnitOfWork).
    - Provides read_all for query-style listing (pagination + sorting).
    Mutating operations must be performed through the UnitOfWork
    (uow.register_new / register_dirty / register_deleted).
    """

    @abstractmethod
    async def read_by_id(
        self,
        user_id: UserId,
        for_update: bool = False,
    ) -> User | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_username(
        self,
        username: Username,
        for_update: bool = False,
    ) -> User | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """
