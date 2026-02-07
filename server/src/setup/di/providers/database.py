import asyncio
import logging
from collections.abc import AsyncIterable, Iterator
from concurrent.futures import ThreadPoolExecutor

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.ports.clock import Clock
from src.infrastructure.adapters.types import HasherSemaphore, HasherThreadPoolExecutor
from src.infrastructure.adapters.utc_clock import UtcClock
from src.setup.config import AppConfig

log = logging.getLogger(__name__)


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    def provide_hasher_threadpool_executor(
        self,
        config: AppConfig,
    ) -> Iterator[HasherThreadPoolExecutor]:
        executor = HasherThreadPoolExecutor(
            ThreadPoolExecutor(
                max_workers=config.security.hasher_max_threads,
                thread_name_prefix="bcrypt",
            )
        )
        yield executor
        executor.shutdown(wait=True, cancel_futures=True)

    @provide(scope=Scope.APP)
    def provide_hasher_semaphore(self, config: AppConfig) -> HasherSemaphore:
        return HasherSemaphore(asyncio.Semaphore(config.security.hasher_max_threads))

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide
    async def get_engine(self, config: AppConfig) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            url=config.database.dsn,
            echo=config.database.echo,
            echo_pool=config.database.echo_pool,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
            pool_timeout=config.database.pool_timeout,
            pool_recycle=config.database.pool_recycle,
        )
        yield engine
        await engine.dispose()

    @provide
    def get_session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide
    def get_clock(self) -> Clock:
        return UtcClock()
