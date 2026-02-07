from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    @property
    @abstractmethod
    def current_time(self) -> datetime: ...
