from src.core.value_objects.user_id import UserId
from src.infrastructure.auth.session.service import AuthSessionService
from src.services.common.ports.identity_provider import IdentityProvider


class AuthSessionIdentityProvider(IdentityProvider):
    def __init__(self, auth_session_service: AuthSessionService) -> None:
        self._auth_session_service = auth_session_service

    async def get_current_user_id(self) -> UserId:
        """:raises AuthenticationError:"""
        return await self._auth_session_service.get_authenticated_user_id()
