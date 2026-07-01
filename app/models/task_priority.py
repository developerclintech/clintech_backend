from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, InternalIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.practice import Practice


class TaskPriority(InternalIdMixin, TimestampMixin, Base):
    __tablename__ = "task_priorities"
    __table_args__ = (
        UniqueConstraint("practice_id", "name", name="uq_task_priorities_practice_id_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    practice_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("practices.id", ondelete="CASCADE"), nullable=False
    )

    practice: Mapped[Practice] = relationship("Practice", lazy="select", foreign_keys=[practice_id])
