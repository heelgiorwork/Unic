from datetime import timedelta
from typing import Literal, cast

from dishka import Provider, Scope, from_context, provide
from fastapi import Request

from src.infrastructure.auth.session.id_generator_str import StrAuthSessionIdGenerator
from src.infrastructure.auth.session.ports.gateway import AuthSessionGateway
from src.infrastructure.auth.session.ports.transport import AuthSessionTransport
from src.infrastructure.auth.session.service import AuthSessionService
from src.infrastructure.auth.session.timer_utc import UtcAuthSessionTimer
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.presentation.http.auth.access_token_processor_jwt import JwtAccessTokenProcessor
from src.presentation.http.auth.adapters.session_transport_jwt_cookie import (
    JwtCookieAuthSessionTransport,
)
from src.presentation.http.auth.cookie_params import CookieParams
from src.setup.config.app import AppConfig


class AuthProvider(Provider):
    scope = Scope.REQUEST

    request = from_context(provides=Request, scope=Scope.REQUEST)

    @provide
    def get_access_token_processor(self, config: AppConfig) -> JwtAccessTokenProcessor:
        return JwtAccessTokenProcessor(
            secret=config.security.secret_key.get_secret_value(),
            algorithm=cast(
                Literal[
                    "HS256",
                    "HS384",
                    "HS512",
                    "RS256",
                    "RS384",
                    "RS512",
                ],
                config.security.algorithm,
            ),
        )

    @provide
    def get_cookie_params(self, config: AppConfig) -> CookieParams:
        return CookieParams(secure=getattr(config.security, "cookie_secure", False))

    @provide
    def get_auth_session_transport(
        self,
        request: Request,
        access_token_processor: JwtAccessTokenProcessor,
        cookie_params: CookieParams,
    ) -> AuthSessionTransport:
        return JwtCookieAuthSessionTransport(request, access_token_processor, cookie_params)

    @provide
    def get_id_generator(self) -> StrAuthSessionIdGenerator:
        return StrAuthSessionIdGenerator()

    @provide
    def get_timer(self, config: AppConfig) -> UtcAuthSessionTimer:
        return UtcAuthSessionTimer(
            timedelta(minutes=config.security.auth_session_ttl_minutes),
            config.security.auth_session_refresh_threshold,
        )

    @provide
    def get_auth_session_service(
        self,
        auth_session_gateway: AuthSessionGateway,
        auth_session_transport: AuthSessionTransport,
        uow: UnitOfWork,
        id_generator: StrAuthSessionIdGenerator,
        timer: UtcAuthSessionTimer,
    ) -> AuthSessionService:
        return AuthSessionService(
            auth_session_gateway=auth_session_gateway,
            auth_session_transport=auth_session_transport,
            uow=uow,
            auth_session_id_generator=id_generator,
            auth_session_timer=timer,
        )
