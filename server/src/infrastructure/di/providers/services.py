from dishka import Provider, Scope, provide

from src.adapters.user_geteway import IUserGeteway
from src.infrastructure.database.uow.uowed import UnitOfWork
from src.services.user import UserService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_service(self, user_geteway: IUserGeteway, uow: UnitOfWork) -> UserService:
        return UserService(user_geteway, uow)
