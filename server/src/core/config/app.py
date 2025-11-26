from typing import Self

from pydantic import Field

from .base import BaseConfig
from .database import DatabaseConfig


class AppConfig(BaseConfig, env_prefix="APP_"):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    @classmethod
    def get(cls) -> Self:
        return cls()
