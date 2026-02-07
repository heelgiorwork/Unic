from typing import Self

from pydantic import Field

from .base import BaseConfig
from .database import DatabaseConfig
from .security import SecurityConfig


class AppConfig(BaseConfig, env_prefix="APP_"):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    @classmethod
    def get(cls) -> Self:
        return cls()
