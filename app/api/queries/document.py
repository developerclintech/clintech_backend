from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentUpdate
from utils.enums import DocumentCategory, DocumentStatus


_SORT_COLUMNS = {
    "created_at": Document.created_at,
    "filename": Document.filename,
    "file_size": Document.file_size,
}


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        filename: str,
        s3_key: str,
        content_type: str,
        file_size: int,
        uploaded_by_id: str,
        practice_id: str | None = None,
        description: str | None = None,
        category: DocumentCategory | None = None,
    ) -> Document:
        doc = Document(
            filename=filename,
            s3_key=s3_key,
            content_type=content_type,
            file_size=file_size,
            uploaded_by_id=uploaded_by_id,
            practice_id=practice_id,
            description=description,
            category=category.value if category else None,
            status=DocumentStatus.PENDING.value,
        )
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def get_by_id(self, document_id: str) -> Document | None:
        result = await self.session.execute(
            select(Document)
            .options(joinedload(Document.practice), joinedload(Document.uploaded_by))
            .where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_ids(self, document_ids: list[str]) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .options(joinedload(Document.practice), joinedload(Document.uploaded_by))
            .where(Document.id.in_(document_ids))
        )
        return list(result.scalars().unique().all())

    async def update(self, doc: Document, payload: DocumentUpdate) -> Document:
        for field, value in payload.model_dump(exclude_none=True).items():
            if isinstance(value, (DocumentCategory, DocumentStatus)):
                value = value.value
            setattr(doc, field, value)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def delete(self, doc: Document) -> None:
        await self.session.delete(doc)
        await self.session.flush()

    async def get_paginated(
        self,
        *,
        page: int,
        page_size: int,
        practice_id: str | None = None,
        category: DocumentCategory | None = None,
        status: DocumentStatus | None = None,
        uploaded_by_id: str | None = None,
        filename: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Document], int]:
        base = select(Document).options(
            joinedload(Document.practice), joinedload(Document.uploaded_by)
        )
        count_base = select(func.count()).select_from(Document)

        if practice_id is not None:
            base = base.where(Document.practice_id == practice_id)
            count_base = count_base.where(Document.practice_id == practice_id)
        if category is not None:
            base = base.where(Document.category == category.value)
            count_base = count_base.where(Document.category == category.value)
        if status is not None:
            base = base.where(Document.status == status.value)
            count_base = count_base.where(Document.status == status.value)
        if uploaded_by_id is not None:
            base = base.where(Document.uploaded_by_id == uploaded_by_id)
            count_base = count_base.where(Document.uploaded_by_id == uploaded_by_id)
        if filename is not None:
            base = base.where(Document.filename.ilike(f"%{filename}%"))
            count_base = count_base.where(Document.filename.ilike(f"%{filename}%"))
        if date_from is not None:
            base = base.where(Document.created_at >= date_from)
            count_base = count_base.where(Document.created_at >= date_from)
        if date_to is not None:
            base = base.where(Document.created_at <= date_to)
            count_base = count_base.where(Document.created_at <= date_to)

        sort_col = _SORT_COLUMNS.get(sort_by, Document.created_at)
        order_expr = sort_col.desc() if sort_order == "desc" else sort_col.asc()

        total = (await self.session.execute(count_base)).scalar_one()

        offset = (page - 1) * page_size
        rows = await self.session.execute(
            base.order_by(order_expr).offset(offset).limit(page_size)
        )
        return list(rows.scalars().unique().all()), total

    async def get_stats(self, practice_id: str | None = None) -> dict:
        total_stmt = select(
            func.count(Document.id),
            func.coalesce(func.sum(Document.file_size), 0),
        ).select_from(Document)
        status_stmt = (
            select(Document.status, func.count(Document.id))
            .select_from(Document)
            .group_by(Document.status)
        )
        category_stmt = (
            select(Document.category, func.count(Document.id))
            .select_from(Document)
            .where(Document.category.isnot(None))
            .group_by(Document.category)
        )

        if practice_id is not None:
            total_stmt = total_stmt.where(Document.practice_id == practice_id)
            status_stmt = status_stmt.where(Document.practice_id == practice_id)
            category_stmt = category_stmt.where(Document.practice_id == practice_id)

        total_count, total_size = (await self.session.execute(total_stmt)).one()
        status_rows = (await self.session.execute(status_stmt)).all()
        category_rows = (await self.session.execute(category_stmt)).all()

        return {
            "total_documents": total_count,
            "total_size_bytes": int(total_size),
            "by_status": [{"status": r[0], "count": r[1]} for r in status_rows],
            "by_category": [{"category": r[0], "count": r[1]} for r in category_rows],
        }
