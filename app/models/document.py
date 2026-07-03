from __future__ import annotations

from uuid import uuid4

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, InternalIdMixin, TimestampMixin
from utils.enums import DocumentCategory, DocumentStatus


class Document(InternalIdMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(127), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=DocumentStatus.PENDING.value)
    uploaded_by_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    practice_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("practices.id", ondelete="SET NULL"), nullable=True
    )

    uploaded_by: Mapped[User] = relationship("User", lazy="select", foreign_keys=[uploaded_by_id])
    practice: Mapped[Practice | None] = relationship("Practice", lazy="select", foreign_keys=[practice_id])
