from uuid import uuid4

from src.core.ports.post_id_generator import PostIdGenerator
from src.core.value_objects.post_id import PostId


class UuidPostIdGenerator(PostIdGenerator):
    def generate(self) -> PostId:
        return PostId(uuid4())
