from __future__ import annotations

import json
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, InternalIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user_practice import UserPractice


class Practice(InternalIdMixin, TimestampMixin, Base):
    __tablename__ = "practices"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ods_code: Mapped[str] = mapped_column(String(20), nullable=False)
    notice: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    practice_hours: Mapped[json] = mapped_column(JSON, nullable=True)
    is_emis_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user_memberships: Mapped[list[UserPractice]] = relationship(
        "UserPractice",
        back_populates="practice",
    )
