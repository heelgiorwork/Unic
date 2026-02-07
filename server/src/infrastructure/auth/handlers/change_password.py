import logging
from dataclasses import dataclass

from src.core.services.user import UserService
from src.core.value_objects.raw_password import RawPassword
from src.infrastructure.auth.exceptions import (
    AuthenticationChangeError,
    ReAuthenticationError,
)
from src.infrastructure.auth.handlers.constants import (
    AUTH_PASSWORD_INVALID,
    AUTH_PASSWORD_NEW_SAME_AS_CURRENT,
)
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.services.common.services.current_user import CurrentUserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangePasswordRequest:
    current_password: str
    new_password: str


class ChangePasswordHandler:
    """
    - Open to authenticated users.
    - The current user can change their password.
    - New password must differ from current password.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        uow: UnitOfWork,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._uow = uow

    async def execute(self, request_data: ChangePasswordRequest) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainTypeError:
        :raises AuthenticationChangeError:
        :raises ReAuthenticationError:
        :raises PasswordHasherBusyError:
        """
        log.info("Change password: started.")

        current_user = await self._current_user_service.get_current_user(for_update=True)

        current_password = RawPassword(request_data.current_password)
        new_password = RawPassword(request_data.new_password)
        if current_password == new_password:
            raise AuthenticationChangeError(AUTH_PASSWORD_NEW_SAME_AS_CURRENT)

        if not await self._user_service.is_password_valid(
            current_user,
            current_password,
        ):
            raise ReAuthenticationError(AUTH_PASSWORD_INVALID)

        await self._user_service.change_password(current_user, new_password)
        async with self._uow:
            pass

        log.info("Change password: done. User ID: '%s'.", current_user.id_.value)
