"""add_documents_table

Revision ID: 202506040001
Revises: ce1b9a583c5a
Create Date: 2026-06-04 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506040001"
down_revision: Union[str, None] = "ce1b9a583c5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("s3_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=127), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("uploaded_by_id", sa.String(length=36), nullable=False),
        sa.Column("practice_id", sa.String(length=36), nullable=True),
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["practice_id"], ["practices.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("internal_id", name="uq_documents_internal_id"),
        sa.UniqueConstraint("s3_key", name="uq_documents_s3_key"),
    )
    op.create_index("ix_documents_practice_id", "documents", ["practice_id"])
    op.create_index("ix_documents_uploaded_by_id", "documents", ["uploaded_by_id"])
    op.create_index("ix_documents_created_at", "documents", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_documents_created_at", table_name="documents")
    op.drop_index("ix_documents_uploaded_by_id", table_name="documents")
    op.drop_index("ix_documents_practice_id", table_name="documents")
    op.drop_table("documents")
