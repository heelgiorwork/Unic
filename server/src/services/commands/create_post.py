from dataclasses import dataclass
from uuid import UUID

from src.core.services.post import PostService
from src.core.value_objects.post_content import PostContent
from src.core.value_objects.post_title import PostTitle
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.services.common.ports.post_command_gateway import PostCommandGateway
from src.services.common.services.authorization.authorize import authorize
from src.services.common.services.authorization.permissions import (
    CanCreatePost,
    PostCreationContext,
)
from src.services.common.services.current_user import CurrentUserService


@dataclass(frozen=True, slots=True)
class CreatePostRequest:
    title: str
    content: str


@dataclass(frozen=True)
class CreatePostResponse:
    id: UUID


class CreatePostInteractor:
    """
    - Создает черновик поста
    - Только PUBLISHER и выше могут создавать посты
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        post_service: PostService,
        post_command_gateway: PostCommandGateway,
        uow: UnitOfWork,
    ):
        self._current_user_service = current_user_service
        self._post_service = post_service
        self._post_command_gateway = post_command_gateway
        self._uow = uow

    async def execute(self, request_data: CreatePostRequest) -> CreatePostResponse:
        current_user = await self._current_user_service.get_current_user()

        authorize(CanCreatePost(), context=PostCreationContext(subject=current_user))

        post = self._post_service.create_draft(
            author_id=current_user.id_,
            title=PostTitle(request_data.title),
            content=PostContent(request_data.content),
        )

        async with self._uow:
            self._uow.register_new(post)

        return CreatePostResponse(id=post.id_.value)
