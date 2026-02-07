from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.core.enums.post_status import PostStatus
from src.core.exceptions.post import PostNotFoundError
from src.core.value_objects.post_id import PostId
from src.services.common.ports.post_command_gateway import PostCommandGateway
from src.services.common.services.current_user import CurrentUserService


@dataclass(frozen=True, slots=True)
class GetPostByIdRequest:
    post_id: UUID


@dataclass(frozen=True, slots=True)
class GetPostByIdResponse:
    id: UUID
    author_id: UUID
    title: str
    content: str
    status: PostStatus
    created_at: datetime


class GetPostByIdInteractor:
    """
    - Отдает полный пост по id
    - Доступно всем пользователям
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        post_gateway: PostCommandGateway,
    ):
        self._current_user_service = current_user_service
        self._post_gateway = post_gateway

    async def execute(self, request: GetPostByIdRequest) -> GetPostByIdResponse:
        await self._current_user_service.get_current_user()

        post = await self._post_gateway.read_by_id(
            PostId(request.post_id),
            for_update=False,
        )

        if post is None:
            raise PostNotFoundError(str(request.post_id))

        return GetPostByIdResponse(
            id=post.id_.value,
            author_id=post.author_id.value,
            title=post.title.value,
            content=post.content.value,
            status=post.status,
            created_at=post.created_at
        )
