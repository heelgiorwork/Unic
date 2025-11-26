# src/infrastructure/database/repositories/user_repository.py
from typing import List, Optional, cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.user_geteway import IUserGeteway
from src.core.entities.user import UserEntity
from src.infrastructure.database.models import User
from src.infrastructure.database.uow.mapper import BaseDataMapper
from src.infrastructure.database.uow.uowed import UnitOfWork, UoWModel


class UserMapper(BaseDataMapper[UserEntity]):
    def __init__(self, session: AsyncSession):
        self.session = session

    def to_orm(self, entity: UserEntity) -> User:
        orm_model = User(
            user_name=entity.user_name,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        if entity.id is not None:
            orm_model.id = entity.id
        return orm_model

    def to_entity(self, orm_model: User) -> UserEntity:
        return UserEntity(
            id=orm_model.id,
            user_name=orm_model.user_name,
            password_hash=orm_model.password_hash,
            full_name=orm_model.full_name,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    async def insert(self, entity: UserEntity) -> None:
        orm_model = self.to_orm(entity)
        self.session.add(orm_model)
        await self.session.flush()
        entity.id = orm_model.id

    async def update(self, entity: UserEntity) -> None:
        if entity.id is None:
            raise ValueError("Cannot update entity without id")

        orm_model = self.to_orm(entity)
        await self.session.merge(orm_model)

    async def delete(self, entity: UserEntity) -> None:
        if entity.id is None:
            raise ValueError("Cannot delete entity without id")

        orm_model = await self.session.get(User, entity.id)
        if orm_model:
            await self.session.delete(orm_model)


class UserRepository(IUserGeteway):
    def __init__(
        self,
        session: AsyncSession,
        uow: UnitOfWork,
    ):
        self.session = session
        self.uow = uow
        self.mapper = UserMapper(self.session)
        self.uow.mappers[UserEntity] = self.mapper

    async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            return None

        entity = self.mapper.to_entity(orm_model)

        return cast(UserEntity, UoWModel(entity, self.uow))

    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        result = await self.session.execute(select(User).where(User.user_name == username))
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            return None

        entity = self.mapper.to_entity(orm_model)
        return cast(UserEntity, UoWModel(entity, self.uow))

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[UserEntity]:
        result = await self.session.execute(select(User).limit(limit).offset(offset))
        orm_models = result.scalars().all()

        return [
            cast(UserEntity, UoWModel(self.mapper.to_entity(orm), self.uow)) for orm in orm_models
        ]

    async def search_by_name(self, name_pattern: str) -> List[UserEntity]:
        result = await self.session.execute(
            select(User).where(User.full_name.ilike(f"%{name_pattern}%"))
        )
        orm_models = result.scalars().all()

        return [
            cast(UserEntity, UoWModel(self.mapper.to_entity(orm), self.uow)) for orm in orm_models
        ]

    async def exists_by_username(self, username: str) -> bool:
        result = await self.session.execute(select(User.id).where(User.user_name == username))
        return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar_one()
