"""add_document_id_to_tasks

Revision ID: 202607230001
Revises: 202507060001
Create Date: 2026-07-23 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202607230001"
down_revision: Union[str, None] = "202507060001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("document_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "fk_tasks_document_id_documents",
        "tasks",
        "documents",
        ["document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_tasks_document_id", "tasks", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_tasks_document_id", table_name="tasks")
    op.drop_constraint("fk_tasks_document_id_documents", "tasks", type_="foreignkey")
    op.drop_column("tasks", "document_id")
