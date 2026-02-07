from dataclasses import dataclass
from uuid import UUID

from src.core.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UserId(ValueObject):
    value: UUID
