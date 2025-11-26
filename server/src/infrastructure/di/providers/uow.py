from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.adapters.user_geteway import IUserGeteway
from src.infrastructure.database.geteway.user_geteway import UserRepository
from src.infrastructure.database.uow.uowed import (
    AbstractUnitOfWorkContext,
    UnitOfWork,
    UnitOfWorkAlchemyContext,
)


class UowProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=AbstractUnitOfWorkContext)
    async def get_context(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[UnitOfWorkAlchemyContext]:
        async with session_factory() as session:
            yield UnitOfWorkAlchemyContext(session)

    @provide(scope=Scope.REQUEST)
    def get_uow(
        self,
        context: AbstractUnitOfWorkContext,
    ) -> UnitOfWork:
        return UnitOfWork(context)

    @provide(scope=Scope.REQUEST)
    def get_user_repository(
        self,
        context: AbstractUnitOfWorkContext,
        uow: UnitOfWork,
    ) -> IUserGeteway:
        return UserRepository(context.session, uow)
