from typing import Any

from src.core.enums.user_role import UserRole
from src.core.exceptions.base import DomainError
from src.core.value_objects.user_id import UserId
from src.core.value_objects.username import Username


class UsernameAlreadyExistsError(DomainError):
    def __init__(self, username: Any) -> None:
        message = f"User with {username!r} already exists."
        super().__init__(message)


class UserNotFoundByIdError(DomainError):
    def __init__(self, user_id: UserId) -> None:
        message = f"User with {user_id.value!r} is not found."
        super().__init__(message)


class UserNotFoundByUsernameError(DomainError):
    def __init__(self, username: Username) -> None:
        message = f"User with {username.value!r} is not found."
        super().__init__(message)


class ActivationChangeNotPermittedError(DomainError):
    def __init__(self, username: Username, role: UserRole) -> None:
        message = (
            f"Changing activation of user {username.value!r} ({role}) is not permitted."
        )
        super().__init__(message)


class RoleAssignmentNotPermittedError(DomainError):
    def __init__(self, role: UserRole) -> None:
        message = f"Assignment of role {role} is not permitted."
        super().__init__(message)


class RoleChangeNotPermittedError(DomainError):
    def __init__(self, username: Username, role: UserRole) -> None:
        message = f"Changing role of user {username.value!r} ({role}) is not permitted."
        super().__init__(message)
