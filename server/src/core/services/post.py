from src.core.entities.post import Post
from src.core.enums.post_status import PostStatus
from src.core.ports.clock import Clock
from src.core.ports.post_id_generator import PostIdGenerator
from src.core.value_objects.post_content import PostContent
from src.core.value_objects.post_title import PostTitle
from src.core.value_objects.user_id import UserId


class PostService:
    def __init__(
        self,
        post_id_generator: PostIdGenerator,
        clock: Clock,
    ):
        self._post_id_generator = post_id_generator
        self._clock = clock

    def create_draft(
        self,
        *,
        author_id: UserId,
        title: PostTitle,
        content: PostContent,
    ) -> Post:
        return Post(
            id_=self._post_id_generator.generate(),
            author_id=author_id,
            title=title,
            content=content,
            created_at=self._clock.current_time,
            status=PostStatus.DRAFT,
        )

    def edit(
        self,
        post: Post,
        *,
        title: PostTitle,
        content: PostContent,
    ) -> bool:
        if post.title.value == title.value and post.content.value == content.value:
            return False

        post.title = title
        post.content = content
        return True

    def publish(self, post: Post) -> bool:
        if post.is_published:
            return False

        post.status = PostStatus.PUBLISHED
        return True
