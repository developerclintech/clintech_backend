from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from utils.enums import DocumentCategory, DocumentStatus


class DocumentUpdate(BaseModel):
    description: str | None = Field(default=None, max_length=500)
    category: DocumentCategory | None = None
    status: DocumentStatus | None = None
    practice_id: str | None = None


class DocumentStatusUpdate(BaseModel):
    status: DocumentStatus


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    content_type: str
    file_size: int
    file_size_display: str | None = None
    file_type: str | None = None
    category: DocumentCategory | None = None
    description: str | None
    status: DocumentStatus = DocumentStatus.PENDING
    uploaded_by_id: str
    uploaded_by_name: str | None = None
    practice_id: str | None
    practice_name: str | None = None
    created_at: datetime
    updated_at: datetime
    download_url: str | None = None


class BulkUploadResponse(BaseModel):
    uploaded: list[DocumentRead]
    failed: list[UploadFailure]


class UploadFailure(BaseModel):
    filename: str
    reason: str


class PaginatedDocumentsResponse(BaseModel):
    items: list[DocumentRead]
    total: int
    page: int
    page_size: int
    pages: int


class StatusCount(BaseModel):
    status: str
    count: int


class CategoryCount(BaseModel):
    category: str
    count: int


class DocumentStats(BaseModel):
    total_documents: int
    total_size_bytes: int
    total_size_display: str
    by_status: list[StatusCount]
    by_category: list[CategoryCount]


class BulkDeleteRequest(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=100)


class BulkDeleteFailure(BaseModel):
    id: str
    reason: str


class BulkDeleteResponse(BaseModel):
    deleted: list[str]
    failed: list[BulkDeleteFailure]
