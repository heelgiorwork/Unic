from dataclasses import dataclass

from src.core.enums.user_role import UserRole
from src.services.common.ports.user_command_gateway import ListUsersQM, UserCommandGateway
from src.services.common.query_params.offset_pagination import OffsetPaginationParams
from src.services.common.query_params.sorting import SortingOrder, SortingParams
from src.services.common.services.authorization.authorize import (
    authorize,
)
from src.services.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from src.services.common.services.current_user import CurrentUserService


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersRequest:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder


class ListUsersQueryService:
    """
    - Open to admins.
    - Retrieves a paginated list of existing users with relevant information.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_gateway: UserCommandGateway,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_gateway = user_gateway

    async def execute(self, request_data: ListUsersRequest) -> ListUsersQM:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises PaginationError:
        :raises SortingError:
        :raises ReaderError:
        """

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )

        pagination = OffsetPaginationParams(
            limit=request_data.limit,
            offset=request_data.offset,
        )
        sorting = SortingParams(
            field=request_data.sorting_field,
            order=request_data.sorting_order,
        )
        response = await self._user_gateway.read_all(
            pagination=pagination,
            sorting=sorting,
        )

        return response
