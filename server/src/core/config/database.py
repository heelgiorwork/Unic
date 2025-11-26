from pydantic import PostgresDsn, SecretStr

from .base import BaseConfig


class DatabaseConfig(BaseConfig, env_prefix="DATABASE_"):
    host: str
    port: int
    name: str
    user: str
    password: SecretStr = SecretStr("secret")

    echo: bool
    echo_pool: bool
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int

    @property
    def dsn(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.name,
        ).unicode_string()
