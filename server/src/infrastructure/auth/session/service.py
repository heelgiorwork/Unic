from datetime import datetime
from typing import Final

from src.core.value_objects.user_id import UserId
from src.infrastructure.auth.exceptions import AuthenticationError
from src.infrastructure.auth.session.id_generator_str import StrAuthSessionIdGenerator
from src.infrastructure.auth.session.model import AuthSession
from src.infrastructure.auth.session.ports.gateway import AuthSessionGateway
from src.infrastructure.auth.session.ports.transport import AuthSessionTransport
from src.infrastructure.auth.session.timer_utc import UtcAuthSessionTimer
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.infrastructure.exceptions.gateway import DataMapperError

AUTH_UNAVAILABLE: Final[str] = "Authentication is currently unavailable. Please try again later."
AUTH_NOT_AUTHENTICATED: Final[str] = "Not authenticated."
AUTH_SESSION_EXPIRED: Final[str] = "Auth session expired."


class AuthSessionService:
    def __init__(
        self,
        auth_session_gateway: AuthSessionGateway,
        auth_session_transport: AuthSessionTransport,
        uow: UnitOfWork,
        auth_session_id_generator: StrAuthSessionIdGenerator,
        auth_session_timer: UtcAuthSessionTimer,
    ) -> None:
        self._gateway = auth_session_gateway
        self._transport = auth_session_transport
        self._uow = uow
        self._id_generator = auth_session_id_generator
        self._timer = auth_session_timer
        self._cached_session: AuthSession | None = None

    async def issue_session(self, user_id: UserId) -> None:
        """Создаёт новую сессию и сохраняет её через UoW"""
        session_id = self._id_generator.generate()
        expiration = self._timer.auth_session_expiration
        session = AuthSession(id_=session_id, user_id=user_id, expiration=expiration)

        try:
            async with self._uow as uow:
                tracked = uow.register_new(session)  # возвращается UoWModel
            self._transport.deliver(tracked)
        except DataMapperError as e:
            raise AuthenticationError(AUTH_UNAVAILABLE) from e

    async def get_authenticated_user_id(self) -> UserId:
        """Возвращает user_id текущей сессии"""
        session = await self._get_current_session()
        session = await self._validate_and_extend_session(session)
        self._cached_session = session
        return session.user_id

    async def terminate_current_session(self) -> None:
        """Удаляет текущую сессию"""
        session_id = (
            self._cached_session.id_ if self._cached_session else self._transport.extract_id()
        )
        if session_id is None:
            return

        self._transport.remove_current()

        try:
            session = await self._gateway.read_by_id(session_id)
            if session:
                async with self._uow as uow:
                    uow.register_deleted(session)
        except DataMapperError:
            pass

        self._cached_session = None

    async def terminate_all_sessions_for_user(self, user_id: UserId) -> None:
        """Удаляет все сессии пользователя"""
        sessions = await self._gateway.read_all_for_user(user_id)
        try:
            async with self._uow as uow:
                for s in sessions:
                    uow.register_deleted(s)
        except DataMapperError:
            raise

        if self._cached_session and self._cached_session.user_id == user_id:
            self._transport.remove_current()
            self._cached_session = None

    async def _get_current_session(self) -> AuthSession:
        """Получает текущую сессию из транспорта или кэша"""
        if self._cached_session:
            return self._cached_session

        session_id = self._transport.extract_id()
        if session_id is None:
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

        try:
            session = await self._gateway.read_by_id(session_id)
        except DataMapperError as e:
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED) from e

        if session is None:
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

        return session

    async def _validate_and_extend_session(self, session: AuthSession) -> AuthSession:
        """Проверяет сессию на истечение и при необходимости продлевает"""
        now = self._timer.current_time

        if session.expiration <= now:
            raise AuthenticationError(AUTH_SESSION_EXPIRED)

        if session.expiration - now > self._timer.refresh_trigger_interval:
            return session

        # Пролонгация сессии
        original_expiration = session.expiration
        session.expiration = self._timer.auth_session_expiration

        try:
            async with self._uow as uow:
                uow.register_dirty(session)  # просто помечаем объект как dirty
        except DataMapperError:
            session.expiration = original_expiration
            return session

        # session уже модифицирован, можно его доставить в транспорт
        self._transport.deliver(session)
        return session
