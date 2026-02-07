import logging
from dataclasses import dataclass
from uuid import UUID

from src.core.entities.user import User
from src.core.enums.user_role import UserRole
from src.core.exceptions.user import UserNotFoundByIdError
from src.core.services.user import UserService
from src.core.value_objects.user_id import UserId
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.services.common.ports.user_command_gateway import UserCommandGateway
from src.services.common.services.authorization.authorize import authorize
from src.services.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from src.services.common.services.current_user import CurrentUserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GrantAdminRequest:
    user_id: UUID


class GrantAdminInteractor:
    """
    - Доступно только супер-администраторам
    - Предоставляет указанный пользователю права администратора
    - Права супер-администратора изменить нельзя
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_command_gateway: UserCommandGateway,
        user_service: UserService,
        uow: UnitOfWork,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_command_gateway = user_command_gateway
        self._user_service = user_service
        self._uow = uow

    async def execute(self, request_data: GrantAdminRequest) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises UserNotFoundByIdError:
        :raises RoleChangeNotPermittedError:
        """
        log.info("Grant admin: started. Target user ID: '%s'.", request_data.user_id)

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.ADMIN,
            ),
        )

        user_id = UserId(request_data.user_id)
        user: User | None = await self._user_command_gateway.read_by_id(
            user_id,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByIdError(user_id)

        if self._user_service.toggle_user_admin_role(user, is_admin=True):
            async with self._uow:
                pass

        log.info("Grant admin: done. Target user ID: '%s'.", user.id_.value)
