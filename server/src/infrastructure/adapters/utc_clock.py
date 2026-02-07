from datetime import datetime

from src.core.constants import TIMEZONE
from src.core.ports.clock import Clock


class UtcClock(Clock):
    @property
    def current_time(self) -> datetime:
        return datetime.now(tz=TIMEZONE)
