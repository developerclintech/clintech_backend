from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202605180001"
down_revision: str | None = "202605160001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("uq_user_practices_user_practice", table_name="user_practices")
    op.create_index(
        "uq_user_practices_user_practice_role",
        "user_practices",
        ["user_id", "practice_id", "role"],
        unique=True,
        postgresql_where=sa.text("practice_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_user_practices_user_practice_role", table_name="user_practices")
    op.create_index(
        "uq_user_practices_user_practice",
        "user_practices",
        ["user_id", "practice_id"],
        unique=True,
        postgresql_where=sa.text("practice_id IS NOT NULL"),
    )
