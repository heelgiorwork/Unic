from abc import abstractmethod

from src.core.value_objects.user_id import UserId


class UserIdGenerator:
    @abstractmethod
    def generate(self) -> UserId: ...
