"""make_task_categories_and_priorities_global

Revision ID: 202507060001
Revises: 202507030002
Create Date: 2026-07-06 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202507060001"
down_revision: Union[str, None] = "202507030002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Names become globally unique: keep the oldest row per name, drop the rest.
    bind.execute(
        sa.text(
            "DELETE FROM task_categories a USING task_categories b "
            "WHERE a.name = b.name AND a.internal_id > b.internal_id"
        )
    )
    bind.execute(
        sa.text(
            "DELETE FROM task_priorities a USING task_priorities b "
            "WHERE a.name = b.name AND a.internal_id > b.internal_id"
        )
    )

    op.drop_index("ix_task_categories_practice_id", table_name="task_categories")
    op.drop_constraint("uq_task_categories_practice_id_name", "task_categories", type_="unique")
    op.drop_column("task_categories", "practice_id")
    op.create_unique_constraint("uq_task_categories_name", "task_categories", ["name"])

    op.drop_index("ix_task_priorities_practice_id", table_name="task_priorities")
    op.drop_constraint("uq_task_priorities_practice_id_name", "task_priorities", type_="unique")
    op.drop_column("task_priorities", "practice_id")
    op.create_unique_constraint("uq_task_priorities_name", "task_priorities", ["name"])


def downgrade() -> None:
    # practice_id values cannot be restored; recreate the column as nullable.
    op.drop_constraint("uq_task_priorities_name", "task_priorities", type_="unique")
    op.add_column("task_priorities", sa.Column("practice_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "task_priorities_practice_id_fkey",
        "task_priorities",
        "practices",
        ["practice_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_task_priorities_practice_id", "task_priorities", ["practice_id"])
    op.create_unique_constraint(
        "uq_task_priorities_practice_id_name", "task_priorities", ["practice_id", "name"]
    )

    op.drop_constraint("uq_task_categories_name", "task_categories", type_="unique")
    op.add_column("task_categories", sa.Column("practice_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "task_categories_practice_id_fkey",
        "task_categories",
        "practices",
        ["practice_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_task_categories_practice_id", "task_categories", ["practice_id"])
    op.create_unique_constraint(
        "uq_task_categories_practice_id_name", "task_categories", ["practice_id", "name"]
    )
