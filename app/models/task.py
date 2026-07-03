from __future__ import annotations

from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, InternalIdMixin, TimestampMixin
from utils.enums import TaskStatus


class Task(InternalIdMixin, TimestampMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=TaskStatus.PENDING.value)

    created_by_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    assigned_to_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    practice_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("practices.id", ondelete="SET NULL"), nullable=True
    )

    created_by: Mapped[User] = relationship("User", lazy="select", foreign_keys=[created_by_id])
    assigned_to: Mapped[User | None] = relationship("User", lazy="select", foreign_keys=[assigned_to_id])
    practice: Mapped[Practice | None] = relationship("Practice", lazy="select", foreign_keys=[practice_id])
