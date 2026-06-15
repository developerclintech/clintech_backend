from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentUpdate
from utils.enums import DocumentCategory, DocumentStatus


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

        total = (await self.session.execute(count_base)).scalar_one()

        offset = (page - 1) * page_size
        rows = await self.session.execute(
            base.order_by(Document.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(rows.scalars().unique().all()), total
