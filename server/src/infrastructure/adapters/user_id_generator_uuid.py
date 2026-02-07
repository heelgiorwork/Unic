from uuid import uuid4

from src.core.ports.user_id_generator import UserIdGenerator
from src.core.value_objects.user_id import UserId


class UuidUserIdGenerator(UserIdGenerator):
    def generate(self) -> UserId:
        return UserId(uuid4())
