from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202605180002"
down_revision: str | None = "202605180001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "password_reset_otps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("delivery_channel", sa.String(length=32), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("otp_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_password_reset_otps_consumed_at"),
        "password_reset_otps",
        ["consumed_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_otps_delivery_channel"),
        "password_reset_otps",
        ["delivery_channel"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_otps_destination"),
        "password_reset_otps",
        ["destination"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_otps_expires_at"),
        "password_reset_otps",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_otps_user_id"),
        "password_reset_otps",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_password_reset_otps_user_id"), table_name="password_reset_otps")
    op.drop_index(
        op.f("ix_password_reset_otps_expires_at"),
        table_name="password_reset_otps",
    )
    op.drop_index(
        op.f("ix_password_reset_otps_destination"),
        table_name="password_reset_otps",
    )
    op.drop_index(
        op.f("ix_password_reset_otps_delivery_channel"),
        table_name="password_reset_otps",
    )
    op.drop_index(
        op.f("ix_password_reset_otps_consumed_at"),
        table_name="password_reset_otps",
    )
    op.drop_table("password_reset_otps")
