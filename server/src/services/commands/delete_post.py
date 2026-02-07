from dataclasses import dataclass
from uuid import UUID

from src.core.exceptions.post import PostNotFoundError
from src.core.value_objects.post_id import PostId
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.services.common.ports.post_command_gateway import PostCommandGateway
from src.services.common.ports.user_command_gateway import UserCommandGateway
from src.services.common.services.authorization.authorize import authorize
from src.services.common.services.authorization.composite import AnyOf
from src.services.common.services.authorization.permissions import (
    CanModifyOwnPost,
    CanModifySubordinatePost,
    PostModificationContext,
)
from src.services.common.services.current_user import CurrentUserService


@dataclass(frozen=True, slots=True)
class DeletePostRequest:
    post_id: UUID


class DeletePostInteractor:
    """
    Удаляет пост.
    - PUBLISHER может удалять только свои посты
    - ADMIN/SUPER_ADMIN могут удалять свои и посты подчиненных
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        post_gateway: PostCommandGateway,
        user_gateway: UserCommandGateway,
        uow: UnitOfWork,
    ):
        self._current_user_service = current_user_service
        self._post_gateway = post_gateway
        self._user_gateway = user_gateway
        self._uow = uow

    async def execute(self, request_data: DeletePostRequest) -> None:
        current_user = await self._current_user_service.get_current_user()

        post = await self._post_gateway.read_by_id(
            PostId(request_data.post_id),
            for_update=True,
        )

        if post is None:
            raise PostNotFoundError(post_id=str(request_data.post_id))

        post_author = await self._user_gateway.read_by_id(
            user_id=post.author_id,
        )

        if post_author is None:
            raise ValueError(f"Post author {post.author_id} not found")

        authorize(
            AnyOf(
                CanModifyOwnPost(),
                CanModifySubordinatePost(),
            ),
            context=PostModificationContext(
                subject=current_user,
                target_post=post,
                post_author=post_author,
            ),
        )

        async with self._uow:
            self._uow.register_deleted(post)
