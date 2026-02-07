import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from src.core.services.user import UserService
from src.core.value_objects.raw_password import RawPassword
from src.core.value_objects.username import Username
from src.infrastructure.auth.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from src.infrastructure.auth.handlers.constants import (
    AUTH_ALREADY_AUTHENTICATED,
)
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.services.common.ports.user_command_gateway import UserCommandGateway
from src.services.common.services.current_user import CurrentUserService


@dataclass(frozen=True, slots=True, kw_only=True)
class SignUpRequest:
    username: str
    password: str


class SignUpResponse(TypedDict):
    id: UUID


class SignUpHandler:
    """
    - Open to everyone.
    - Registers a new user with validation and uniqueness checks.
    - Passwords are peppered, salted, and stored as hashes.
    - A logged-in user cannot sign up until the session expires or is terminated.
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

    async def execute(self, request_data: SignUpRequest) -> SignUpResponse:
        """
        :raises AlreadyAuthenticatedError:
        :raises AuthorizationError:
        :raises DataMapperError:
        :raises DomainTypeError:
        :raises PasswordHasherBusyError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """

        try:
            await self._current_user_service.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except AuthenticationError:
            pass

        username = Username(request_data.username)
        password = RawPassword(request_data.password)

        user = await self._user_service.create_user(username, password)

        async with self._uow:
            self._uow.register_new(user)

        return SignUpResponse(id=user.id_.value)
