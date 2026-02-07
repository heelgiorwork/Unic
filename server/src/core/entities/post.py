from datetime import datetime

from src.core.entities.base import Entity
from src.core.enums.post_status import PostStatus
from src.core.value_objects.post_content import PostContent
from src.core.value_objects.post_id import PostId
from src.core.value_objects.post_title import PostTitle
from src.core.value_objects.user_id import UserId


class Post(Entity[PostId]):
    def __init__(
        self,
        *,
        id_: PostId,
        author_id: UserId,
        title: PostTitle,
        content: PostContent,
        created_at: datetime,
        status: PostStatus = PostStatus.DRAFT,
    ):
        super().__init__(id_=id_)
        self.author_id = author_id
        self.title = title
        self.content = content
        self.created_at = created_at
        self.status = status

    @property
    def is_published(self) -> bool:
        return self.status == PostStatus.PUBLISHED
