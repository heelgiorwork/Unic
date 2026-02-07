from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums.user_role import UserRole
from src.core.ports.password_hasher import PasswordHasher
from src.core.ports.user_id_generator import UserIdGenerator
from src.core.value_objects.raw_password import RawPassword
from src.infrastructure.adapters.password_hasher_bcrypt import BcryptPasswordHasher
from src.infrastructure.adapters.user_id_generator_uuid import UuidUserIdGenerator
from src.infrastructure.database.persistence_sqla.models.user import UserORM
from src.setup.config.app import AppConfig


async def on_startup(container: AsyncContainer) -> None:
    async with container() as scope:
        session = await scope.get(AsyncSession)
        hasher = await scope.get(PasswordHasher)
        id_generator = await scope.get(UserIdGenerator)
        config = await scope.get(AppConfig)

        async with session.begin():
            await init_superadmin(
                session=session,
                hasher=hasher,
                id_generator=id_generator,
                config=config,
            )


async def init_superadmin(
    session: AsyncSession,
    hasher: BcryptPasswordHasher,
    id_generator: UuidUserIdGenerator,
    config: AppConfig,
) -> None:
    result = await session.execute(
        select(UserORM).where(UserORM.role == UserRole.SUPER_ADMIN.value).limit(1)
    )

    if result.scalar_one_or_none():
        return

    password_hash = hasher.hash_sync(RawPassword(config.security.superadmin_password))

    session.add(
        UserORM(
            id=id_generator.generate().value,
            username=config.security.superadmin_username,
            password_hash=password_hash.value,
            role=UserRole.SUPER_ADMIN.value,
            is_active=True,
        )
    )
