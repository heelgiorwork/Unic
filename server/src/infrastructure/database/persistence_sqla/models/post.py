from datetime import datetime
from uuid import UUID as PYUUID

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums.post_status import PostStatus
from src.core.value_objects.post_content import PostContent
from src.core.value_objects.post_title import PostTitle
from src.infrastructure.database.persistence_sqla.models.base import Base


class PostORM(Base):
    __tablename__ = "posts"

    id: Mapped[PYUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(PostTitle.MAX_LEN),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text(PostContent.MAX_LEN),
        nullable=False,
    )

    author_id: Mapped[PYUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
