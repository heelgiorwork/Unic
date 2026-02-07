from src.infrastructure.auth.session.service import AuthSessionService
from src.services.common.services.current_user import CurrentUserService


class LogOutHandler:
    """
    - Open to authenticated users.
    - Logs the user out by deleting the JWT access token from cookies
    and removing the session from the database.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        auth_session_service: AuthSessionService,
    ) -> None:
        self._current_user_service = current_user_service
        self._auth_session_service = auth_session_service

    async def execute(self) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """

        current_user = await self._current_user_service.get_current_user()

        await self._auth_session_service.terminate_current_session()
