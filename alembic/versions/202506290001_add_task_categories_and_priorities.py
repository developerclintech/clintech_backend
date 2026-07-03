"""add_task_categories_and_priorities

Revision ID: 202506290001
Revises: 202506180001
Create Date: 2026-06-29 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "202506290001"
down_revision: Union[str, None] = "202506180001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_CATEGORIES = ["administrative", "clinical", "billing", "follow_up", "referral", "other"]
DEFAULT_PRIORITIES = ["low", "medium", "high", "urgent"]


def upgrade() -> None:
    op.create_table(
        "task_categories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("practice_id", sa.String(length=36), nullable=False),
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["practice_id"], ["practices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("internal_id", name="uq_task_categories_internal_id"),
        sa.UniqueConstraint("practice_id", "name", name="uq_task_categories_practice_id_name"),
    )
    op.create_index("ix_task_categories_practice_id", "task_categories", ["practice_id"])

    op.create_table(
        "task_priorities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("practice_id", sa.String(length=36), nullable=False),
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["practice_id"], ["practices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("internal_id", name="uq_task_priorities_internal_id"),
        sa.UniqueConstraint("practice_id", "name", name="uq_task_priorities_practice_id_name"),
    )
    op.create_index("ix_task_priorities_practice_id", "task_priorities", ["practice_id"])

    bind = op.get_bind()
    practices = sa.table("practices", sa.column("id", sa.String))
    task_categories = sa.table(
        "task_categories",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("practice_id", sa.String),
    )
    task_priorities = sa.table(
        "task_priorities",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("practice_id", sa.String),
    )

    practice_ids = [row[0] for row in bind.execute(sa.select(practices.c.id))]
    for practice_id in practice_ids:
        bind.execute(
            task_categories.insert(),
            [{"id": str(uuid4()), "name": name, "practice_id": practice_id} for name in DEFAULT_CATEGORIES],
        )
        bind.execute(
            task_priorities.insert(),
            [{"id": str(uuid4()), "name": name, "practice_id": practice_id} for name in DEFAULT_PRIORITIES],
        )


def downgrade() -> None:
    op.drop_index("ix_task_priorities_practice_id", table_name="task_priorities")
    op.drop_table("task_priorities")
    op.drop_index("ix_task_categories_practice_id", table_name="task_categories")
    op.drop_table("task_categories")
