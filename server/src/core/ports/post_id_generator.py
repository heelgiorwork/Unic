from abc import abstractmethod

from src.core.value_objects.post_id import PostId


class PostIdGenerator:
    @abstractmethod
    def generate(self) -> PostId: ...
