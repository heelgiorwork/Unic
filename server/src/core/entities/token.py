from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserTokenEntity:
    id: int | None
    user_id: int
    refresh_token_hash: str
    created_at: datetime
    expires_at: datetime
    is_revoked: bool = False
