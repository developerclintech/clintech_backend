"""add_category_and_status_to_documents

Revision ID: 202506080001
Revises: 202506040001
Create Date: 2026-06-08 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506080001"
down_revision: Union[str, None] = "202506040001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("category", sa.String(length=50), nullable=True))
    op.add_column(
        "documents",
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
    )
    op.alter_column("documents", "status", server_default=None)
    op.create_index("ix_documents_category", "documents", ["category"])
    op.create_index("ix_documents_status", "documents", ["status"])


def downgrade() -> None:
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_index("ix_documents_category", table_name="documents")
    op.drop_column("documents", "status")
    op.drop_column("documents", "category")
