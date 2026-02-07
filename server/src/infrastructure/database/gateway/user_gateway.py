from typing import List, Optional, cast

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.user import User
from src.core.exceptions.user import UsernameAlreadyExistsError
from src.core.value_objects.user_id import UserId
from src.core.value_objects.user_password_hash import UserPasswordHash
from src.core.value_objects.username import Username
from src.infrastructure.database.persistence_sqla.models.user import UserORM
from src.infrastructure.database.uow.mapper import BaseDataMapper
from src.infrastructure.database.uow.uowed import UnitOfWork, UoWModel
from src.services.common.exceptions.query import SortingError
from src.services.common.ports.user_command_gateway import (
    ListUsersQM,
    UserQueryModel,
)
from src.services.common.query_params.offset_pagination import OffsetPaginationParams
from src.services.common.query_params.sorting import SortingParams


class UserMapper(BaseDataMapper[User]):
    def __init__(self, session: AsyncSession):
        self.session = session

    def to_orm(self, entity: User) -> UserORM:
        return UserORM(
            id=entity.id_.value,
            username=entity.username.value,
            password_hash=entity.password_hash.value,
            role=entity.role,
            is_active=entity.is_active,
        )

    def to_entity(self, orm: UserORM) -> User:
        return User(
            id_=UserId(orm.id),
            username=Username(orm.username),
            password_hash=UserPasswordHash(orm.password_hash),
            role=orm.role,
            is_active=orm.is_active,
        )

    async def insert(self, entity: User) -> None:
        try:
            orm_model = self.to_orm(entity)
            self.session.add(orm_model)
            await self.session.flush()
        except IntegrityError as e:
            raise UsernameAlreadyExistsError(entity.username.value) from e

    async def update(self, entity: User) -> None:
        orm_model = self.to_orm(entity)
        await self.session.merge(orm_model)

    async def delete(self, entity: User) -> None:
        orm_id = entity.id_.value
        if orm_id is None:
            raise ValueError("Cannot delete entity without id")
        await self.session.execute(delete(UserORM).where(UserORM.id == orm_id))


class UserRepository:
    def __init__(self, session: AsyncSession, uow: UnitOfWork):
        self.session = session
        self.uow = uow

        self.mapper = UserMapper(session)
        self.uow.mappers[User] = self.mapper

    async def read_by_id(self, user_id: UserId, for_update: bool = False) -> Optional[User]:
        raw_id = user_id.value if isinstance(user_id, UserId) else user_id

        stmt = select(UserORM).where(UserORM.id == raw_id)
        orm = (await self.session.execute(stmt)).scalar_one_or_none()

        if orm is None:
            return None

        entity = self.mapper.to_entity(orm)
        return cast(User, UoWModel(entity, self.uow))

    async def read_by_username(
        self,
        username: Username,
        for_update: bool = False,
    ) -> Optional[User]:
        value = username.value

        stmt = select(UserORM).where(UserORM.username == value)
        orm = (await self.session.execute(stmt)).scalar_one_or_none()

        if orm is None:
            return None

        entity = self.mapper.to_entity(orm)
        return cast(User, UoWModel(entity, self.uow))

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(UserORM.id).where(UserORM.username == username)
        return (await self.session.execute(stmt)).scalar_one_or_none() is not None

    async def read_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQM:
        field_map = {
            "id": UserORM.id,
            "id_": UserORM.id,
            "username": UserORM.username,
            "role": UserORM.role,
            "is_active": UserORM.is_active,
        }

        if sorting.field not in field_map:
            raise SortingError(f"Unknown sorting field: {sorting.field}")

        column = field_map[sorting.field]
        order = column.asc() if sorting.order.value == "ASC" else column.desc()

        stmt = select(UserORM).order_by(order).limit(pagination.limit).offset(pagination.offset)

        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        users = [
            cast(
                User,
                UoWModel(self.mapper.to_entity(orm), self.uow),
            )
            for orm in orms
        ]

        total = await self.session.scalar(select(func.count()).select_from(UserORM))

        users_list: List[UserQueryModel] = [
            {
                "id_": u.id_.value,
                "username": u.username.value,
                "role": u.role,
                "is_active": u.is_active,
            }
            for u in users
        ]

        return {
            "users": users_list,
            "total": total or 0,
        }
