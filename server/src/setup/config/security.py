from pydantic import SecretStr

from .base import BaseConfig


class SecurityConfig(BaseConfig, env_prefix="SECURITY_"):
    secret_key: SecretStr
    algorithm: str

    access_token_expire_minutes: int
    refresh_token_expire_days: int

    cookie_secure: bool

    auth_session_ttl_minutes: int
    auth_session_refresh_threshold: float

    password_pepper: str
    hasher_work_factor: int
    hasher_max_threads: int
    hasher_semaphore_wait_timeout_s: float

    superadmin_username: str = "superadmin"
    superadmin_password: str
