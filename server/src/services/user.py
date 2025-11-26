from datetime import datetime, timezone
from typing import List

from src.adapters.user_geteway import IUserGeteway
from src.core.entities.user import UserEntity
from src.infrastructure.database.uow.uowed import UnitOfWork


class UserService:
    def __init__(self, user_geteway: IUserGeteway, uow: UnitOfWork):
        self.user_geteway = user_geteway
        self.uow = uow

    async def create_user(self, username: str, password_hash: str, full_name: str) -> UserEntity:
        existing = await self.user_geteway.get_by_username(username)
        if existing:
            raise ValueError(f"User with username '{username}' already exists")

        now = datetime.now(timezone.utc)
        entity = UserEntity(
            id=None,
            user_name=username,
            password_hash=password_hash,
            full_name=full_name,
            created_at=now,
            updated_at=now,
        )

        async with self.uow as uow:
            tracked_entity = uow.register_new(entity)

        return tracked_entity

    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        return await self.user_geteway.get_by_id(user_id)

    async def get_user_by_username(self, username: str) -> UserEntity | None:
        return await self.user_geteway.get_by_username(username)

    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[UserEntity]:
        return await self.user_geteway.get_all(limit=limit, offset=offset)

    async def search_users_by_name(self, name_pattern: str) -> List[UserEntity]:
        if not name_pattern or len(name_pattern.strip()) == 0:
            raise ValueError("Search pattern cannot be empty")
        return await self.user_geteway.search_by_name(name_pattern)

    async def update_user_full_name(self, user_id: int, new_full_name: str) -> UserEntity:
        entity = await self.user_geteway.get_by_id(user_id)
        if not entity:
            raise ValueError(f"User with id {user_id} not found")

        async with self.uow:
            entity.full_name = new_full_name
            entity.updated_at = datetime.now(timezone.utc)

        return entity

    async def update_user_username(self, user_id: int, new_username: str) -> UserEntity:
        existing = await self.user_geteway.get_by_username(new_username)
        if existing and existing.id != user_id:
            raise ValueError(f"Username '{new_username}' is already taken")

        entity = await self.user_geteway.get_by_id(user_id)
        if not entity:
            raise ValueError(f"User with id {user_id} not found")

        async with self.uow:
            entity.user_name = new_username
            entity.updated_at = datetime.now(timezone.utc)

        return entity

    async def change_user_password(self, user_id: int, new_password_hash: str) -> UserEntity:
        entity = await self.user_geteway.get_by_id(user_id)
        if not entity:
            raise ValueError(f"User with id {user_id} not found")

        async with self.uow:
            entity.password_hash = new_password_hash
            entity.updated_at = datetime.now(timezone.utc)

        return entity

    async def update_user(
        self,
        user_id: int,
        full_name: str | None = None,
        username: str | None = None,
    ) -> UserEntity:
        entity = await self.user_geteway.get_by_id(user_id)
        if not entity:
            raise ValueError(f"User with id {user_id} not found")

        if username and username != entity.user_name:
            existing = await self.user_geteway.get_by_username(username)
            if existing:
                raise ValueError(f"Username '{username}' is already taken")

        async with self.uow:
            if full_name is not None:
                entity.full_name = full_name
            if username is not None:
                entity.user_name = username
            entity.updated_at = datetime.now(timezone.utc)

        return entity

    async def delete_user(self, user_id: int) -> None:
        entity = await self.user_geteway.get_by_id(user_id)
        if not entity:
            raise ValueError(f"User with id {user_id} not found")

        async with self.uow as uow:
            uow.register_deleted(entity)

    async def delete_user_by_username(self, username: str) -> None:
        entity = await self.user_geteway.get_by_username(username)
        if not entity:
            raise ValueError(f"User with username '{username}' not found")

        async with self.uow as uow:
            uow.register_deleted(entity)

    async def verify_user_password(self, username: str, password_hash: str) -> bool:
        entity = await self.user_geteway.get_by_username(username)
        if not entity:
            return False
        return entity.password_hash == password_hash

    async def check_username_available(self, username: str) -> bool:
        return not await self.user_geteway.exists_by_username(username)

    async def get_user_count(self) -> int:
        return await self.user_geteway.count()

    async def create_multiple_users(self, users_data: List[dict]) -> List[UserEntity]:
        usernames = [data["username"] for data in users_data]
        if len(usernames) != len(set(usernames)):
            raise ValueError("Duplicate usernames in batch")

        for username in usernames:
            if await self.user_geteway.exists_by_username(username):
                raise ValueError(f"Username '{username}' already exists")

        now = datetime.now(timezone.utc)
        entities = []
        async with self.uow as uow:
            for data in users_data:
                entity = UserEntity(
                    id=None,
                    user_name=data["username"],
                    password_hash=data["password_hash"],
                    full_name=data["full_name"],
                    created_at=now,
                    updated_at=now,
                )
                tracked = uow.register_new(entity)
                entities.append(tracked)

        return entities

    async def delete_multiple_users(self, user_ids: List[int]) -> int:
        deleted_count = 0
        async with self.uow as uow:
            for user_id in user_ids:
                entity = await self.user_geteway.get_by_id(user_id)
                if entity:
                    uow.register_deleted(entity)
                    deleted_count += 1
        return deleted_count
