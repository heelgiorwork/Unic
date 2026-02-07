from typing import Optional, cast

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.value_objects.user_id import UserId
from src.infrastructure.auth.session.model import AuthSession
from src.infrastructure.auth.session.ports.gateway import AuthSessionGateway
from src.infrastructure.database.persistence_sqla.models.auth_session import AuthSessionORM
from src.infrastructure.database.uow.mapper import BaseDataMapper
from src.infrastructure.database.uow.uowed import UnitOfWork, UoWModel


class AuthSessionMapper(BaseDataMapper[AuthSession]):
    def __init__(self, session: AsyncSession):
        self.session = session

    def to_orm(self, entity: AuthSession) -> AuthSessionORM:
        return AuthSessionORM(
            id=entity.id_,
            user_id=entity.user_id.value,
            expiration=entity.expiration,
        )

    def to_entity(self, orm: AuthSessionORM) -> AuthSession:
        return AuthSession(
            id_=orm.id,
            user_id=UserId(orm.user_id),
            expiration=orm.expiration,
        )

    async def insert(self, entity: AuthSession) -> None:
        orm_model = self.to_orm(entity)
        self.session.add(orm_model)
        await self.session.flush()

    async def update(self, entity: AuthSession) -> None:
        orm_model = self.to_orm(entity)
        await self.session.merge(orm_model)

    async def delete(self, entity: AuthSession) -> None:
        await self.session.execute(
            delete(AuthSessionORM).where(AuthSessionORM.id == entity.id_)
        )


class AuthSessionGatewayImpl(AuthSessionGateway):
    def __init__(self, session: AsyncSession, uow: UnitOfWork):
        self.session = session
        self.uow = uow

        mapper = AuthSessionMapper(session)
        self.uow.mappers[AuthSession] = mapper
        self.mapper = mapper

    async def read_by_id(self, auth_session_id: str) -> Optional[AuthSession]:
        stmt = select(AuthSessionORM).where(AuthSessionORM.id == auth_session_id)
        orm = (await self.session.execute(stmt)).scalar_one_or_none()

        if orm is None:
            return None

        entity = self.mapper.to_entity(orm)
        return cast(AuthSession, UoWModel(entity, self.uow))

    async def read_all_for_user(self, user_id: UserId) -> list[AuthSession]:
        stmt = select(AuthSessionORM).where(AuthSessionORM.user_id == user_id.value)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            cast(AuthSession, UoWModel(self.mapper.to_entity(orm), self.uow))
            for orm in orms
        ]

    async def delete_all_for_user(self, user_id: UserId) -> None:
        await self.session.execute(
            delete(AuthSessionORM).where(AuthSessionORM.user_id == user_id.value)
        )
