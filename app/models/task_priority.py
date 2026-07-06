from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, InternalIdMixin, TimestampMixin


class TaskPriority(InternalIdMixin, TimestampMixin, Base):
    __tablename__ = "task_priorities"
    __table_args__ = (
        UniqueConstraint("name", name="uq_task_priorities_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
