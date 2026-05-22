from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202605160001"
down_revision: str | None = "202605150001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("fk_patients_practice_id_practices", "patients", type_="foreignkey")
    op.drop_index(op.f("ix_patients_practice_id"), table_name="patients")
    op.drop_index(op.f("ix_patients_status"), table_name="patients")
    op.drop_index(op.f("ix_patients_medical_record_number"), table_name="patients")
    op.drop_table("patients")


def downgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("medical_record_number", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("practice_id", sa.String(length=36), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["practice_id"],
            ["practices.id"],
            name="fk_patients_practice_id_practices",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_patients_medical_record_number"),
        "patients",
        ["medical_record_number"],
        unique=True,
    )
    op.create_index(op.f("ix_patients_status"), "patients", ["status"], unique=False)
    op.create_index(
        op.f("ix_patients_practice_id"), "patients", ["practice_id"], unique=False
    )
