from typing import Optional, cast

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.post import Post
from src.core.enums.post_status import PostStatus
from src.core.value_objects.post_content import PostContent
from src.core.value_objects.post_id import PostId
from src.core.value_objects.post_title import PostTitle
from src.core.value_objects.user_id import UserId
from src.infrastructure.database.persistence_sqla.models.post import PostORM
from src.infrastructure.database.uow.mapper import BaseDataMapper
from src.infrastructure.database.uow.uowed import UnitOfWork, UoWModel
from src.services.common.exceptions.query import SortingError
from src.services.common.ports.post_command_gateway import (
    ListPostsQM,
    PostQM,
)
from src.services.common.query_params.offset_pagination import OffsetPaginationParams
from src.services.common.query_params.sorting import SortingParams


class PostMapper(BaseDataMapper[Post]):
    def __init__(self, session: AsyncSession):
        self.session = session

    def to_orm(self, entity: Post) -> PostORM:
        return PostORM(
            id=entity.id_.value,
            title=entity.title.value,
            content=entity.content.value,
            author_id=entity.author_id.value,
            status=entity.status,
            created_at=entity.created_at,
        )

    def to_entity(self, orm: PostORM) -> Post:
        return Post(
            id_=PostId(orm.id),
            title=PostTitle(orm.title),
            content=PostContent(orm.content),
            author_id=UserId(orm.author_id),
            status=orm.status,
            created_at=orm.created_at,
        )

    async def insert(self, entity: Post) -> None:
        self.session.add(self.to_orm(entity))
        await self.session.flush()

    async def update(self, entity: Post) -> None:
        await self.session.merge(self.to_orm(entity))

    async def delete(self, entity: Post) -> None:
        await self.session.execute(delete(PostORM).where(PostORM.id == entity.id_.value))


class PostRepository:
    def __init__(self, session: AsyncSession, uow: UnitOfWork):
        self.session = session
        self.uow = uow
        self.mapper = PostMapper(session)
        self.uow.mappers[Post] = self.mapper

    async def read_by_id(self, post_id: PostId, for_update: bool = False) -> Optional[Post]:
        stmt = select(PostORM).where(PostORM.id == post_id.value)
        orm = (await self.session.execute(stmt)).scalar_one_or_none()
        if orm is None:
            return None
        return cast(Post, UoWModel(self.mapper.to_entity(orm), self.uow))

    async def read_all(
        self,
        *,
        author_id: UserId | None = None,
        status: PostStatus | None = None,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListPostsQM:
        field_map = {
            "id": PostORM.id,
            "id_": PostORM.id,
            "title": PostORM.title,
            "author_id": PostORM.author_id,
            "status": PostORM.status,
        }

        if sorting.field not in field_map:
            raise SortingError(f"Unknown sorting field: {sorting.field}")

        column = field_map[sorting.field]
        order = column.asc() if sorting.order.value == "ASC" else column.desc()

        stmt = select(PostORM)

        if author_id is not None:
            stmt = stmt.where(PostORM.author_id == author_id.value)
        if status is not None:
            stmt = stmt.where(PostORM.status == status)

        stmt = stmt.order_by(order).limit(pagination.limit).offset(pagination.offset)

        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        posts_list: list[PostQM] = [
            {
                "id_": orm.id,
                "title": orm.title,
                "author_id": orm.author_id,
                "status": orm.status,
            }
            for orm in orms
        ]

        total = await self.session.scalar(select(func.count()).select_from(PostORM))

        return {"posts": posts_list, "total": total or 0}
