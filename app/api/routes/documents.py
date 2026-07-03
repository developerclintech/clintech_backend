from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import RedirectResponse

from app.api.blc.document import DocumentService
from app.api.deps import get_document_service
from app.models.user import User
from app.schemas.document import (
    BulkDeleteRequest,
    BulkDeleteResponse,
    BulkUploadResponse,
    DocumentRead,
    DocumentStats,
    DocumentStatusUpdate,
    DocumentUpdate,
    PaginatedDocumentsResponse,
)
from utils.apis_mapping import (
    DOCUMENT_BULK_DELETE_ROLES,
    DOCUMENT_DELETE_ROLES,
    DOCUMENT_EDIT_ROLES,
    DOCUMENT_READ_ROLES,
    DOCUMENT_STATS_ROLES,
    DOCUMENT_UPLOAD_ROLES,
)
from utils.auth_functions import require_roles
from utils.enums import DocumentCategory, DocumentStatus

router = APIRouter()


_CATEGORY_ENUM = [e.value for e in DocumentCategory]

_UPLOAD_SCHEMA = {
    "requestBody": {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "required": ["files"],
                    "properties": {
                        "files": {
                            "type": "array",
                            "items": {"type": "string", "format": "binary"},
                            "description": "One or more files to upload",
                        },
                        "practice_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        "description": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        "category": {
                            "anyOf": [
                                {"type": "string", "enum": _CATEGORY_ENUM},
                                {"type": "null"},
                            ]
                        },
                    },
                }
            }
        },
    }
}


@router.post(
    "/upload",
    response_model=BulkUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload one or more documents",
    openapi_extra=_UPLOAD_SCHEMA,
)
async def upload_documents(
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_UPLOAD_ROLES))],
    files: list[UploadFile] = File(..., description="One or more files to upload"),
    practice_id: str | None = Form(default=None),
    description: str | None = Form(default=None),
    category: DocumentCategory | None = Form(default=None),
) -> BulkUploadResponse:
    return await service.upload_documents(
        files=files,
        current_user=current_user,
        practice_id=practice_id,
        description=description,
        category=category,
    )


@router.post(
    "/bulk-delete",
    response_model=BulkDeleteResponse,
    summary="Delete multiple documents by ID (admin only)",
)
async def bulk_delete_documents(
    payload: BulkDeleteRequest,
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_BULK_DELETE_ROLES))],
) -> BulkDeleteResponse:
    return await service.bulk_delete_documents(payload.ids, current_user)


@router.get(
    "/stats",
    response_model=DocumentStats,
    summary="Document counts and storage summary",
)
async def get_document_stats(
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_STATS_ROLES))],
    practice_id: Annotated[str | None, Query()] = None,
) -> DocumentStats:
    return await service.get_stats(current_user, practice_id=practice_id)


@router.get(
    "",
    response_model=PaginatedDocumentsResponse,
    summary="List uploaded documents (paginated)",
)
async def list_documents(
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_READ_ROLES))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    practice_id: Annotated[str | None, Query()] = None,
    category: Annotated[DocumentCategory | None, Query()] = None,
    status: Annotated[DocumentStatus | None, Query()] = None,
    uploaded_by_id: Annotated[str | None, Query()] = None,
    filename: Annotated[str | None, Query(description="Partial filename search")] = None,
    date_from: Annotated[datetime | None, Query(description="Filter by upload date (from, inclusive)")] = None,
    date_to: Annotated[datetime | None, Query(description="Filter by upload date (to, inclusive)")] = None,
    sort_by: Annotated[Literal["created_at", "filename", "file_size"], Query()] = "created_at",
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "desc",
) -> PaginatedDocumentsResponse:
    return await service.list_documents(
        current_user=current_user,
        page=page,
        page_size=page_size,
        practice_id=practice_id,
        category=category,
        status=status,
        uploaded_by_id=uploaded_by_id,
        filename=filename,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Get document details and a pre-signed download URL",
)
async def get_document(
    document_id: str,
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_READ_ROLES))],
) -> DocumentRead:
    return await service.get_document(document_id, current_user)


@router.get(
    "/{document_id}/download",
    summary="Redirect to a fresh pre-signed S3 download URL",
    response_class=RedirectResponse,
    status_code=302,
)
async def download_document(
    document_id: str,
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_READ_ROLES))],
) -> RedirectResponse:
    url = await service.get_presigned_url(document_id, current_user)
    return RedirectResponse(url=url, status_code=302)


@router.patch(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Update document metadata",
)
async def update_document(
    document_id: str,
    payload: DocumentUpdate,
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_EDIT_ROLES))],
) -> DocumentRead:
    return await service.update_document(document_id, payload, current_user)


@router.patch(
    "/{document_id}/status",
    response_model=DocumentRead,
    summary="Change the status of a document",
)
async def change_document_status(
    document_id: str,
    payload: DocumentStatusUpdate,
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_EDIT_ROLES))],
) -> DocumentRead:
    return await service.change_document_status(document_id, payload.status, current_user)


@router.put(
    "/{document_id}/file",
    response_model=DocumentRead,
    summary="Replace the file content of an existing document",
)
async def replace_document_file(
    document_id: str,
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_EDIT_ROLES))],
    file: UploadFile = File(..., description="Replacement file"),
) -> DocumentRead:
    return await service.replace_document_file(document_id, file, current_user)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
)
async def delete_document(
    document_id: str,
    service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(require_roles(DOCUMENT_DELETE_ROLES))],
) -> None:
    await service.delete_document(document_id, current_user)
