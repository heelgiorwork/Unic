from uuid import UUID as PYUUID

from sqlalchemy import Boolean, Enum, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums.user_role import UserRole
from src.core.value_objects.username import Username
from src.infrastructure.database.persistence_sqla.models.base import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[PYUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(
        String(Username.MAX_LEN),
        nullable=False,
        unique=True,
    )
    password_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
