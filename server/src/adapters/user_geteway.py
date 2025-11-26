from abc import ABC, abstractmethod
from typing import List, Optional

from src.core.entities.user import UserEntity


class IUserGeteway(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[UserEntity]: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[UserEntity]: ...

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[UserEntity]: ...

    @abstractmethod
    async def search_by_name(self, name_pattern: str) -> List[UserEntity]: ...

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool: ...

    @abstractmethod
    async def count(self) -> int: ...
