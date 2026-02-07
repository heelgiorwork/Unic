from src.services.common.exceptions.base import ApplicationError


class PaginationError(ApplicationError):
    pass


class SortingError(ApplicationError):
    pass
