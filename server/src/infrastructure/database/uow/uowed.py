from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Self, Type, cast

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.uow.mapper import BaseDataMapper


class UoWModel[T]:
    _model: T
    _uow: "UnitOfWork"

    def __init__(self, model: T, uow: Any) -> None:
        object.__setattr__(self, "_model", model)
        object.__setattr__(self, "_uow", uow)

    def __getattr__(self, key: str) -> Any:
        return getattr(self._model, key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            object.__setattr__(self, key, value)
            return

        setattr(self._model, key, value)
        self._uow.register_dirty(self._model)

    def __getattribute__(self, name: str) -> Any:
        if name == "__class__":
            model = object.__getattribute__(self, "_model")
            return model.__class__
        return object.__getattribute__(self, name)


class AbstractUnitOfWorkContext[T](ABC):
    @abstractmethod
    async def on_enter(self, uow: "UnitOfWork") -> None: ...

    @abstractmethod
    async def on_exit(
        self,
        uow: "UnitOfWork",
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> None: ...


class UnitOfWork:
    def __init__(
        self,
        context: AbstractUnitOfWorkContext,
    ) -> None:
        self.new: Dict[int, Any] = {}
        self.dirty: Dict[int, Any] = {}
        self.deleted: Dict[int, Any] = {}
        self.mappers: Dict[type, BaseDataMapper] = {}
        self.context = context

    def register_new[T](self, model: T) -> T:
        self.new[id(model)] = model
        return cast(T, UoWModel(model, self))

    def register_dirty[T](self, model: T) -> None:
        if isinstance(model, UoWModel):
            model = model._model

        if id(model) in self.new:
            return
        self.dirty[id(model)] = model

    def register_deleted(self, model: Any) -> None:
        if isinstance(model, UoWModel):
            model = model._model

        if id(model) in self.new:
            self.new.pop(id(model))
            return
        if id(model) in self.dirty:
            self.dirty.pop(id(model))
        self.deleted[id(model)] = model

    async def commit(self) -> None:
        grouped: Dict[type, tuple[List, List, List]] = {}

        for model in self.new.values():
            grouped.setdefault(type(model), ([], [], []))[0].append(model)
        for model in self.dirty.values():
            grouped.setdefault(type(model), ([], [], []))[1].append(model)
        for model in self.deleted.values():
            grouped.setdefault(type(model), ([], [], []))[2].append(model)

        for model_type, (new, dirty, deleted) in grouped.items():
            if model_type not in self.mappers:
                raise ValueError(f"Mapper for {model_type.__name__} not registered")

            mapper = self.mappers[model_type]

            for model in new:
                await mapper.insert(model)

            for model in dirty:
                await mapper.update(model)

            for model in deleted:
                await mapper.delete(model)

        self.new.clear()
        self.dirty.clear()
        self.deleted.clear()

    async def __aenter__(self) -> Self:
        if self.context:
            await self.context.on_enter(self)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> None:
        if self.context:
            await self.context.on_exit(self, exc_type, exc_val, exc_tb)


class UnitOfWorkAlchemyContext(AbstractUnitOfWorkContext):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def on_enter(self, uow: UnitOfWork) -> None: ...

    async def on_exit(
        self,
        uow: UnitOfWork,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> None:
        try:
            if exc_type:
                await self.session.rollback()
                return

            if uow.new or uow.dirty or uow.deleted:
                await uow.commit()
                await self.session.commit()
            else:
                await self.session.close()

        except:
            await self.session.rollback()
            raise
