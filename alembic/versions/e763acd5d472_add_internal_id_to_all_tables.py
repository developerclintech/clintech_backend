"""add_internal_id_to_all_tables

Revision ID: e763acd5d472
Revises: 7f49516727ef
Create Date: 2026-05-21 20:46:40.200839

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e763acd5d472'
down_revision: Union[str, None] = '7f49516727ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('audit_logs', sa.Column('internal_id', sa.BigInteger(), sa.Identity(always=False), nullable=False))
    op.create_unique_constraint('uq_audit_logs_internal_id', 'audit_logs', ['internal_id'])
    op.add_column('password_reset_otps', sa.Column('internal_id', sa.BigInteger(), sa.Identity(always=False), nullable=False))
    op.create_unique_constraint('uq_password_reset_otps_internal_id', 'password_reset_otps', ['internal_id'])
    op.add_column('practices', sa.Column('internal_id', sa.BigInteger(), sa.Identity(always=False), nullable=False))
    op.create_unique_constraint('uq_practices_internal_id', 'practices', ['internal_id'])
    op.add_column('user_practices', sa.Column('internal_id', sa.BigInteger(), sa.Identity(always=False), nullable=False))
    op.create_unique_constraint('uq_user_practices_internal_id', 'user_practices', ['internal_id'])
    op.add_column('users', sa.Column('internal_id', sa.BigInteger(), sa.Identity(always=False), nullable=False))
    op.create_unique_constraint('uq_users_internal_id', 'users', ['internal_id'])


def downgrade() -> None:
    op.drop_constraint('uq_users_internal_id', 'users', type_='unique')
    op.drop_column('users', 'internal_id')
    op.drop_constraint('uq_user_practices_internal_id', 'user_practices', type_='unique')
    op.drop_column('user_practices', 'internal_id')
    op.drop_constraint('uq_practices_internal_id', 'practices', type_='unique')
    op.drop_column('practices', 'internal_id')
    op.drop_constraint('uq_password_reset_otps_internal_id', 'password_reset_otps', type_='unique')
    op.drop_column('password_reset_otps', 'internal_id')
    op.drop_constraint('uq_audit_logs_internal_id', 'audit_logs', type_='unique')
    op.drop_column('audit_logs', 'internal_id')
