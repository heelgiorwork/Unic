from abc import ABC, abstractmethod


class BaseDataMapper[T](ABC):
    @abstractmethod
    async def insert(self, model: T) -> None: ...

    @abstractmethod
    async def delete(self, model: T) -> None: ...

    @abstractmethod
    async def update(self, model: T) -> None: ...
