"""Import all ORM models to register them with SQLAlchemy."""


def map_tables() -> None:
    """Import all ORM models to ensure they are registered with the mapper registry."""
    from src.infrastructure.database.persistence_sqla.models.auth_session import (  # noqa: F401, PLC0415
        AuthSessionORM,
    )
    from src.infrastructure.database.persistence_sqla.models.user import (  # noqa: F401, PLC0415
        UserORM,
    )
