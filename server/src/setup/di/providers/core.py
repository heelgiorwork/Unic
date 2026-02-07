from dishka import Provider, Scope, provide, provide_all

from src.core.ports.password_hasher import PasswordHasher
from src.core.ports.post_id_generator import PostIdGenerator
from src.core.ports.user_id_generator import UserIdGenerator
from src.core.services.post import PostService
from src.core.services.user import UserService
from src.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)
from src.infrastructure.adapters.post_id_generator_uuid import UuidPostIdGenerator
from src.infrastructure.adapters.types import HasherSemaphore, HasherThreadPoolExecutor
from src.infrastructure.adapters.user_id_generator_uuid import (
    UuidUserIdGenerator,
)
from src.setup.config.app import AppConfig
from src.setup.config.security import SecurityConfig


class CoreProvider(Provider):
    scope = Scope.APP

    user_service = provide_all(
        UserService,
    )

    post_service = provide_all(
        PostService,
    )

    user_id_generator = provide(UuidUserIdGenerator, provides=UserIdGenerator)
    post_id_generator = provide(UuidPostIdGenerator, provides=PostIdGenerator)

    @provide
    def provide_security_config(self, app_config: AppConfig) -> SecurityConfig:
        return app_config.security

    @provide
    def provide_password_hasher(
        self,
        app_config: AppConfig,
        executor: HasherThreadPoolExecutor,
        semaphore: HasherSemaphore,
    ) -> PasswordHasher:
        return BcryptPasswordHasher(
            pepper=app_config.security.password_pepper.encode(),
            work_factor=app_config.security.hasher_work_factor,
            executor=executor,
            semaphore=semaphore,
            semaphore_wait_timeout_s=app_config.security.hasher_semaphore_wait_timeout_s,
        )
