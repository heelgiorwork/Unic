from dataclasses import dataclass
from uuid import UUID

from src.core.exceptions.post import PostNotFoundError
from src.core.services.post import PostService
from src.core.value_objects.post_content import PostContent
from src.core.value_objects.post_id import PostId
from src.core.value_objects.post_title import PostTitle
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
class EditPostRequest:
    post_id: UUID
    title: str
    content: str


class EditPostInteractor:
    """
    Редактирует пост.
    - PUBLISHER может редактировать только свои посты
    - ADMIN/SUPER_ADMIN могут редактировать свои и посты подчиненных
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        post_service: PostService,
        post_gateway: PostCommandGateway,
        user_gateway: UserCommandGateway,
        uow: UnitOfWork,
    ):
        self._current_user_service = current_user_service
        self._post_service = post_service
        self._post_gateway = post_gateway
        self._user_gateway = user_gateway
        self._uow = uow

    async def execute(self, request_data: EditPostRequest) -> None:

        current_user = await self._current_user_service.get_current_user()

        post = await self._post_gateway.read_by_id(
            post_id=PostId(request_data.post_id),
            for_update=True,
        )

        if post is None:
            raise PostNotFoundError(str(request_data.post_id))

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
            self._post_service.edit(
                post,
                title=PostTitle(request_data.title),
                content=PostContent(request_data.content),
            )
            self._uow.register_dirty(post)
