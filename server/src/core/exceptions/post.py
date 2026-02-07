from src.core.exceptions.base import DomainError


class PostError(DomainError):
    def __init__(self, message: str = "", post_id: str | None = None):
        super().__init__(message)
        self.post_id = post_id

    def __str__(self) -> str:
        base = super().__str__()
        if self.post_id is not None:
            return f"{base} (Post ID: {self.post_id})"
        return base


class PostPublishNotPermittedError(PostError):
    pass


class PostEditNotPermittedError(PostError):
    pass


class PostNotFoundError(PostError):
    def __init__(self, post_id: str):
        super().__init__("Post not found", post_id=post_id)
