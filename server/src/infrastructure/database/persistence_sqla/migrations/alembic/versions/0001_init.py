"""init (users, roles, posts, user_roles, auth_sessions)

Revision ID: 0001
Revises:
Create Date: 2026-02-05 12:00:00.000000
"""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Roles ---
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Добавляем сразу роли
    op.bulk_insert(
        sa.table(
            "roles",
            sa.column("name", sa.String),
            sa.column("description", sa.String),
        ),
        [
            {"name": "super_admin", "description": "Super administrator"},
            {"name": "publisher", "description": "Publisher with content rights"},
        ],
    )

    # --- Users ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("username", sa.String(length=30), nullable=False, unique=True),
        sa.Column("password_hash", sa.LargeBinary(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("USER", "ADMIN", "SUPER_ADMIN", "PUBLISHER", name="userrole"),
            nullable=False,
            server_default="USER",
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()
        ),
    )

    # --- Posts ---
    op.create_table(
        "posts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "author_id",
            UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "PUBLISHED", "ARCHIVED", name="post_status"),
            nullable=False,
            index=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )

    # --- User Roles ---
    op.create_table(
        "user_roles",
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    # --- Auth Sessions ---
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("expiration", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("auth_sessions")
    op.drop_table("user_roles")
    op.drop_table("posts")
    op.drop_table("users")
    op.drop_table("roles")
