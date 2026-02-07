from src.core.value_objects.user_id import UserId
from src.infrastructure.auth.session.service import AuthSessionService
from src.services.common.ports.access_revoker import AccessRevoker


class AuthSessionAccessRevoker(AccessRevoker):
    def __init__(self, auth_session_service: AuthSessionService) -> None:
        self._auth_session_service = auth_session_service

    async def remove_all_user_access(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
        await self._auth_session_service.terminate_all_sessions_for_user(user_id)
