from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, String, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, InternalIdMixin, TimestampMixin
from app.models.password_reset_otp import PasswordResetOtp

if TYPE_CHECKING:
    from app.models.user_practice import UserPractice


class User(InternalIdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    sex_at_birth: Mapped[str] = mapped_column(String(20), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    required_relogin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sds_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    practice_memberships: Mapped[list["UserPractice"]] = relationship(
        "UserPractice",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    password_reset_otps: Mapped[list[PasswordResetOtp]] = relationship(
        "PasswordResetOtp",
        back_populates="user",
        cascade="all, delete-orphan",
    )
