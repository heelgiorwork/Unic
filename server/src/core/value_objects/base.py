from dataclasses import dataclass, fields
from typing import Any, Self


@dataclass(frozen=True, slots=True, repr=False)
class ValueObject:
    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is ValueObject:
            raise TypeError("Base ValueObject cannot be instantiated directly.")
        if not fields(cls):
            raise TypeError(f"{cls.__name__} must have at least one field!")
        return object.__new__(cls)

    def __post_init__(self) -> None:
        ...

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__repr_value()})"

    def __repr_value(self) -> str:
        items = [f for f in fields(self) if f.repr]
        if not items:
            return "<hidden>"
        return ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in items)
