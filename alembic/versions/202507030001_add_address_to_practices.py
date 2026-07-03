"""add_address_to_practices

Revision ID: 202507030001
Revises: 202506290001
Create Date: 2026-07-03 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '202507030001'
down_revision: Union[str, None] = '202506290001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('practices', sa.Column('address', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('practices', 'address')
