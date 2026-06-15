from __future__ import annotations

import math
import re

from fastapi import HTTPException, UploadFile, status

from app.api.queries.document import DocumentRepository
from app.core import s3
from app.models.user import User
from app.schemas.document import (
    BulkUploadResponse,
    DocumentRead,
    DocumentUpdate,
    PaginatedDocumentsResponse,
    UploadFailure,
)
from utils.enums import DocumentCategory, DocumentStatus

_SAFE_FILENAME = re.compile(r"[^\w.\-]")
_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

_MIME_TO_LABEL: dict[str, str] = {
    "application/pdf": "PDF",
    "application/msword": "DOC",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "application/vnd.ms-excel": "XLS",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",
    "text/plain": "TXT",
    "text/csv": "CSV",
    "image/jpeg": "JPEG",
    "image/png": "PNG",
}


def _sanitize(filename: str) -> str:
    return _SAFE_FILENAME.sub("_", filename)


def _build_s3_key(document_id: str, filename: str, practice_id: str | None) -> str:
    scope = practice_id or "global"
    return f"documents/{scope}/{document_id}/{_sanitize(filename)}"


def _file_type_label(filename: str, content_type: str) -> str:
    if "." in filename:
        return filename.rsplit(".", 1)[-1].upper()
    return _MIME_TO_LABEL.get(content_type, content_type.split("/")[-1].upper())


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 ** 2:
        return f"{round(size_bytes / 1024)} KB"
    return f"{size_bytes / 1024 ** 2:.1f} MB"


def _enrich(doc_read: DocumentRead, practice_name: str | None, filename: str, content_type: str, file_size: int) -> DocumentRead:
    doc_read.practice_name = practice_name
    doc_read.file_type = _file_type_label(filename, content_type)
    doc_read.file_size_display = _format_size(file_size)
    return doc_read


class DocumentService:
    def __init__(self, *, documents: DocumentRepository) -> None:
        self.documents = documents

    async def upload_documents(
        self,
        files: list[UploadFile],
        current_user: User,
        practice_id: str | None = None,
        description: str | None = None,
        category: DocumentCategory | None = None,
    ) -> BulkUploadResponse:
        uploaded: list[DocumentRead] = []
        failed: list[UploadFailure] = []

        for file in files:
            filename = file.filename or "unnamed"
            try:
                content = await file.read()
                if len(content) > _MAX_FILE_SIZE:
                    failed.append(
                        UploadFailure(
                            filename=filename,
                            reason=f"File exceeds the 50 MB limit ({len(content)} bytes).",
                        )
                    )
                    continue

                content_type = file.content_type or "application/octet-stream"

                doc = await self.documents.create(
                    filename=filename,
                    s3_key="pending",
                    content_type=content_type,
                    file_size=len(content),
                    uploaded_by_id=current_user.id,
                    practice_id=practice_id,
                    description=description,
                    category=category,
                )

                s3_key = _build_s3_key(doc.id, filename, practice_id)
                s3.upload_file(content, s3_key, content_type)

                doc.s3_key = s3_key
                await self.documents.session.flush()
                await self.documents.session.refresh(doc)

                read = DocumentRead.model_validate(doc)
                read.download_url = s3.generate_presigned_url(s3_key)
                _enrich(read, None, filename, content_type, len(content))
                uploaded.append(read)

            except RuntimeError as exc:
                failed.append(UploadFailure(filename=filename, reason=str(exc)))
            finally:
                await file.seek(0)

        return BulkUploadResponse(uploaded=uploaded, failed=failed)

    async def list_documents(
        self,
        current_user: User,
        page: int,
        page_size: int,
        practice_id: str | None = None,
        category: DocumentCategory | None = None,
        status: DocumentStatus | None = None,
    ) -> PaginatedDocumentsResponse:
        docs, total = await self.documents.get_paginated(
            page=page,
            page_size=page_size,
            practice_id=practice_id,
            category=category,
            status=status,
        )
        items: list[DocumentRead] = []
        for doc in docs:
            read = DocumentRead.model_validate(doc)
            practice_name = doc.practice.name if doc.practice else None
            _enrich(read, practice_name, doc.filename, doc.content_type, doc.file_size)
            items.append(read)

        return PaginatedDocumentsResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if page_size else 0,
        )

    async def get_document(self, document_id: str, current_user: User) -> DocumentRead:
        doc = await self.documents.get_by_id(document_id)
        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )
        read = DocumentRead.model_validate(doc)
        practice_name = doc.practice.name if doc.practice else None
        _enrich(read, practice_name, doc.filename, doc.content_type, doc.file_size)
        try:
            read.download_url = s3.generate_presigned_url(doc.s3_key)
        except RuntimeError:
            read.download_url = None
        return read

    async def update_document(
        self, document_id: str, payload: DocumentUpdate, current_user: User
    ) -> DocumentRead:
        doc = await self.documents.get_by_id(document_id)
        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )
        doc = await self.documents.update(doc, payload)
        read = DocumentRead.model_validate(doc)
        practice_name = doc.practice.name if doc.practice else None
        _enrich(read, practice_name, doc.filename, doc.content_type, doc.file_size)
        try:
            read.download_url = s3.generate_presigned_url(doc.s3_key)
        except RuntimeError:
            read.download_url = None
        return read

    async def delete_document(self, document_id: str, current_user: User) -> None:
        doc = await self.documents.get_by_id(document_id)
        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )
        try:
            s3.delete_file(doc.s3_key)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc
        await self.documents.delete(doc)
