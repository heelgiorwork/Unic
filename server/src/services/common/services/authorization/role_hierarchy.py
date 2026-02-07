from collections.abc import Mapping
from typing import Final

from src.core.enums.user_role import UserRole

SUBORDINATE_ROLES: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.SUPER_ADMIN: {UserRole.ADMIN, UserRole.PUBLISHER, UserRole.USER},
    UserRole.ADMIN: {UserRole.PUBLISHER, UserRole.USER},
    UserRole.PUBLISHER: set(),
    UserRole.USER: set(),
}
