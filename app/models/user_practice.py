from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Boolean, Enum, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, InternalIdMixin, TimestampMixin
from app.models.practice import Practice
from app.models.user import User
from utils.enums import UserRole


class UserPractice(InternalIdMixin, TimestampMixin, Base):
    __tablename__ = "user_practices"
    __table_args__ = (
        Index(
            "uq_user_practices_user_practice_role",
            "user_id",
            "practice_id",
            "role",
            unique=True,
            postgresql_where=text("practice_id IS NOT NULL"),
        ),
        Index(
            "uq_user_practices_user_global_role",
            "user_id",
            "role",
            unique=True,
            postgresql_where=text("practice_id IS NULL"),
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    practice_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("practices.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="practice_memberships")
    practice: Mapped[Practice | None] = relationship(
        "Practice",
        back_populates="user_memberships",
    )
