import re
from dataclasses import dataclass
from typing import ClassVar, Final

from src.core.exceptions.base import DomainTypeError
from src.core.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class Username(ValueObject):

    MIN_LEN: ClassVar[Final[int]] = 3
    MAX_LEN: ClassVar[Final[int]] = 20
    PATTERN: ClassVar[Final[re.Pattern[str]]] = re.compile(r"^[a-zA-Z0-9]+$")

    value: str

    def __post_init__(self) -> None:
        length = len(self.value)

        if length < self.MIN_LEN or length > self.MAX_LEN:
            raise DomainTypeError(
                f"Username must be between {self.MIN_LEN} and {self.MAX_LEN} characters."
            )

        if not self.PATTERN.fullmatch(self.value):
            raise DomainTypeError(
                "Username can only contain letters (A-Z, a-z) and digits (0-9)."
            )
