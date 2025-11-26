from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserEntity:
    id: int | None
    user_name: str
    password_hash: str
    full_name: str
    created_at: datetime
    updated_at: datetime
