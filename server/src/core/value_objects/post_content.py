from dataclasses import dataclass
from typing import ClassVar, Final

from src.core.exceptions.base import DomainTypeError


@dataclass(frozen=True, slots=True, repr=False)
class PostContent:
    MIN_LEN: ClassVar[Final[int]] = 100
    MAX_LEN: ClassVar[Final[int]] = 10_000

    value: str

    def __post_init__(self) -> None:
        length = len(self.value)

        if length < self.MIN_LEN or length > self.MAX_LEN:
            raise DomainTypeError(
                f"Post content must be between {self.MIN_LEN} and {self.MAX_LEN} characters"
            )
