from dataclasses import dataclass
from typing import ClassVar, Final

from src.core.exceptions.base import DomainTypeError
from src.core.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class PostTitle(ValueObject):
    MIN_LEN: ClassVar[Final[int]] = 3
    MAX_LEN: ClassVar[Final[int]] = 255

    value: str

    def __post_init__(self) -> None:
        length = len(self.value)

        if length < self.MIN_LEN or length > self.MAX_LEN:
            raise DomainTypeError(
                f"Post title must be between {self.MIN_LEN} and {self.MAX_LEN} characters"
            )
