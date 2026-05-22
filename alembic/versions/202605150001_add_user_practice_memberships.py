from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "202605150001"
down_revision: str | None = "0307314d1439"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

USER_ROLE_ENUM = sa.Enum(
    "super_admin",
    "practice_admin",
    "doctor",
    "receptionist",
    "staff",
    name="userrole",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "user_practices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("practice_id", sa.String(length=36), nullable=True),
        sa.Column("role", USER_ROLE_ENUM, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
        sa.ForeignKeyConstraint(["practice_id"], ["practices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_practices_practice_id"),
        "user_practices",
        ["practice_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_practices_role"),
        "user_practices",
        ["role"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_practices_user_id"),
        "user_practices",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "uq_user_practices_user_practice",
        "user_practices",
        ["user_id", "practice_id"],
        unique=True,
        postgresql_where=sa.text("practice_id IS NOT NULL"),
    )
    op.create_index(
        "uq_user_practices_user_global_role",
        "user_practices",
        ["user_id", "role"],
        unique=True,
        postgresql_where=sa.text("practice_id IS NULL"),
    )

    user_practices = sa.table(
        "user_practices",
        sa.column("id", sa.String),
        sa.column("user_id", sa.String),
        sa.column("practice_id", sa.String),
        sa.column("role", USER_ROLE_ENUM),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    conn = op.get_bind()
    existing_users = conn.execute(
        sa.text(
            """
            SELECT id, practice_id, role, is_active
            FROM users
            WHERE role = 'super_admin' OR practice_id IS NOT NULL
            """
        )
    ).mappings()
    now = datetime.now(timezone.utc)
    memberships = [
        {
            "id": str(uuid4()),
            "user_id": row["id"],
            "practice_id": None if row["role"] == "super_admin" else row["practice_id"],
            "role": row["role"],
            "is_active": row["is_active"],
            "created_at": now,
            "updated_at": now,
        }
        for row in existing_users
    ]
    if memberships:
        op.bulk_insert(user_practices, memberships)

    op.add_column("patients", sa.Column("practice_id", sa.String(length=36), nullable=True))
    op.create_index(op.f("ix_patients_practice_id"), "patients", ["practice_id"], unique=False)
    op.create_foreign_key(
        "fk_patients_practice_id_practices",
        "patients",
        "practices",
        ["practice_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.drop_index(op.f("ix_users_practice_id"), table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_constraint("users_practice_id_fkey", "users", type_="foreignkey")
    op.drop_column("users", "practice_id")
    op.drop_column("users", "role")


def downgrade() -> None:
    op.add_column("users", sa.Column("role", USER_ROLE_ENUM, nullable=True))
    op.add_column("users", sa.Column("practice_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "users_practice_id_fkey",
        "users",
        "practices",
        ["practice_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        """
        UPDATE users
        SET role = restored.role,
            practice_id = restored.practice_id
        FROM (
            SELECT DISTINCT ON (user_id)
                user_id,
                role,
                practice_id
            FROM user_practices
            WHERE is_active = true
            ORDER BY
                user_id,
                CASE
                    WHEN practice_id IS NULL AND role = 'super_admin' THEN 0
                    ELSE 1
                END,
                created_at
        ) AS restored
        WHERE users.id = restored.user_id
        """
    )
    op.execute("UPDATE users SET role = 'staff' WHERE role IS NULL")
    op.alter_column("users", "role", existing_type=USER_ROLE_ENUM, nullable=False)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_practice_id"), "users", ["practice_id"], unique=False)

    op.drop_constraint("fk_patients_practice_id_practices", "patients", type_="foreignkey")
    op.drop_index(op.f("ix_patients_practice_id"), table_name="patients")
    op.drop_column("patients", "practice_id")

    op.drop_index("uq_user_practices_user_global_role", table_name="user_practices")
    op.drop_index("uq_user_practices_user_practice", table_name="user_practices")
    op.drop_index(op.f("ix_user_practices_user_id"), table_name="user_practices")
    op.drop_index(op.f("ix_user_practices_role"), table_name="user_practices")
    op.drop_index(op.f("ix_user_practices_practice_id"), table_name="user_practices")
    op.drop_table("user_practices")
