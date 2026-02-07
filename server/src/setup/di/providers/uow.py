from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.auth.session.ports.gateway import AuthSessionGateway
from src.infrastructure.database.gateway.auth_session_gateway import (
    AuthSessionGatewayImpl,
)
from src.infrastructure.database.gateway.post_gateway import PostRepository
from src.infrastructure.database.gateway.user_gateway import UserRepository
from src.infrastructure.database.uow.uowed import (
    UnitOfWork,
    UnitOfWorkAlchemyContext,
)
from src.services.common.ports.post_command_gateway import PostCommandGateway
from src.services.common.ports.user_command_gateway import UserCommandGateway


class UowProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=UnitOfWorkAlchemyContext)
    async def get_context(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[UnitOfWorkAlchemyContext]:
        async with session_factory() as session:
            yield UnitOfWorkAlchemyContext(session)

    @provide(scope=Scope.REQUEST)
    def get_uow(
        self,
        context: UnitOfWorkAlchemyContext,
    ) -> UnitOfWork:
        return UnitOfWork(context)

    @provide(scope=Scope.REQUEST)
    def get_user_repository(
        self,
        context: UnitOfWorkAlchemyContext,
        uow: UnitOfWork,
    ) -> UserCommandGateway:
        return UserRepository(context.session, uow)

    @provide(scope=Scope.REQUEST)
    def get_auth_session_gateway(
        self,
        context: UnitOfWorkAlchemyContext,
        uow: UnitOfWork,
    ) -> AuthSessionGateway:
        return AuthSessionGatewayImpl(context.session, uow)

    @provide(scope=Scope.REQUEST)
    def get_posts_gateway(
        self,
        context: UnitOfWorkAlchemyContext,
        uow: UnitOfWork,
    ) -> PostCommandGateway:
        return PostRepository(context.session, uow)
