import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from src.core.enums.user_role import UserRole
from src.core.services.user import UserService
from src.core.value_objects.raw_password import RawPassword
from src.core.value_objects.username import Username
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.services.common.ports.user_command_gateway import UserCommandGateway
from src.services.common.services.authorization.authorize import (
    authorize,
)
from src.services.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from src.services.common.services.current_user import CurrentUserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    username: str
    password: str
    role: UserRole


class CreateUserResponse(TypedDict):
    id: UUID


class CreateUserInteractor:
    """
    - Доступно для админов и супер-админов
    - Создает нового пользователя
    - Роль текущего пользователя должна быть выше роли создаваемого пользователя
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_command_gateway: UserCommandGateway,
        uow: UnitOfWork,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._user_command_gateway = user_command_gateway
        self._uow = uow

    async def execute(self, request_data: CreateUserRequest) -> CreateUserResponse:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainTypeError:
        :raises PasswordHasherBusyError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        log.info("Create user: started. Target username: '%s'.", request_data.username)

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=request_data.role,
            ),
        )

        username = Username(request_data.username)
        password = RawPassword(request_data.password)
        user = await self._user_service.create_user(username, password, request_data.role)

        async with self._uow:
            self._uow.register_new(user)

        log.info("Create user: done. Target username: '%s'.", user.username.value)
        return CreateUserResponse(id=user.id_.value)
