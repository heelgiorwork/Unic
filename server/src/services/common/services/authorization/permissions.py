from collections.abc import Mapping
from dataclasses import dataclass

from src.core.entities.post import Post
from src.core.entities.user import User
from src.core.enums.user_role import UserRole
from src.services.common.services.authorization.base import (
    Permission,
    PermissionContext,
)
from src.services.common.services.authorization.role_hierarchy import (
    SUBORDINATE_ROLES,
)


@dataclass(frozen=True, kw_only=True)
class UserManagementContext(PermissionContext):
    subject: User
    target: User


class CanManageSelf(Permission[UserManagementContext]):
    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        return context.subject == context.target


class CanManageSubordinate(Permission[UserManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target.role in allowed_roles


@dataclass(frozen=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    subject: User
    target_role: UserRole


class CanManageRole(Permission[RoleManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: RoleManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target_role in allowed_roles


@dataclass(frozen=True, kw_only=True)
class PostCreationContext(PermissionContext):
    subject: User


class CanCreatePost(Permission[PostCreationContext]):
    def is_satisfied_by(self, context: PostCreationContext) -> bool:
        return context.subject.role in {
            UserRole.PUBLISHER,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        }



@dataclass(frozen=True, kw_only=True)
class PostModificationContext(PermissionContext):
    subject: User
    target_post: Post
    post_author: User


class CanModifyOwnPost(Permission[PostModificationContext]):
    def is_satisfied_by(self, context: PostModificationContext) -> bool:
        return context.target_post.author_id == context.subject.id_ and context.subject.role in {
            UserRole.PUBLISHER,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        }


class CanModifySubordinatePost(Permission[PostModificationContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: PostModificationContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.post_author.role in allowed_roles
