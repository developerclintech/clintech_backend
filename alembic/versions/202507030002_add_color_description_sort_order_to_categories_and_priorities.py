"""add_color_description_sort_order_to_categories_and_priorities

Revision ID: 202507030002
Revises: 202507030001
Create Date: 2026-07-03 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202507030002"
down_revision: Union[str, None] = "202507030001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("task_categories", sa.Column("color", sa.String(length=7), nullable=True))
    op.add_column("task_categories", sa.Column("description", sa.Text(), nullable=True))

    op.add_column("task_priorities", sa.Column("color", sa.String(length=7), nullable=True))
    op.add_column("task_priorities", sa.Column("sort_order", sa.Integer(), nullable=True))
    op.add_column("task_priorities", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("task_priorities", "description")
    op.drop_column("task_priorities", "sort_order")
    op.drop_column("task_priorities", "color")

    op.drop_column("task_categories", "description")
    op.drop_column("task_categories", "color")
