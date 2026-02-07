from dishka import Provider, Scope, provide, provide_all

from src.infrastructure.auth.adapters.access_revoker import (
    AuthSessionAccessRevoker,
)
from src.infrastructure.auth.adapters.identity_provider import (
    AuthSessionIdentityProvider,
)
from src.services.commands.activate_user import ActivateUserInteractor
from src.services.commands.create_post import CreatePostInteractor
from src.services.commands.create_user import CreateUserInteractor
from src.services.commands.deactivate_user import DeactivateUserInteractor
from src.services.commands.delete_post import DeletePostInteractor
from src.services.commands.edit_post import EditPostInteractor
from src.services.commands.get_post import GetPostByIdInteractor
from src.services.commands.grant_admin import GrantAdminInteractor
from src.services.commands.publish_post import PublishPostInteractor
from src.services.commands.revoke_admin import RevokeAdminInteractor
from src.services.commands.set_user_password import SetUserPasswordInteractor
from src.services.common.ports.access_revoker import AccessRevoker
from src.services.common.ports.identity_provider import IdentityProvider
from src.services.common.services.current_user import CurrentUserService
from src.services.queries.list_posts import ListPostsQueryService
from src.services.queries.list_users import ListUsersQueryService


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Services
    services = provide_all(
        CurrentUserService,
    )

    # Ports Persistence
    # Use the same repository for command reads and query reads until a dedicated
    # query gateway is implemented. `UserRepository` provides read_by_id,
    # read_by_username and also implements a `read_all` method (see implementation
    # in `src/infrastructure/database/gateway/user_gateway.py`).

    # Ports Auth
    access_revoker = provide(AuthSessionAccessRevoker, provides=AccessRevoker)
    identity_provider = provide(AuthSessionIdentityProvider, provides=IdentityProvider)

    # Commands
    commands = provide_all(
        ActivateUserInteractor,
        SetUserPasswordInteractor,
        CreateUserInteractor,
        DeactivateUserInteractor,
        GrantAdminInteractor,
        RevokeAdminInteractor,
        CreatePostInteractor,
        DeletePostInteractor,
        EditPostInteractor,
        PublishPostInteractor,
        GetPostByIdInteractor,
    )

    # Queries
    query_services = provide_all(
        ListUsersQueryService,
        ListPostsQueryService,
    )
