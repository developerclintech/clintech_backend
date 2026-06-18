from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.api.blc.document import DocumentService
from app.api.deps import get_document_service
from app.models.user import User
from app.schemas.document import BulkUploadResponse, DocumentRead, DocumentStatusUpdate, DocumentUpdate, PaginatedDocumentsResponse
from utils.apis_mapping import (
    DOCUMENT_DELETE_ROLES,
    DOCUMENT_EDIT_ROLES,
    DOCUMENT_READ_ROLES,
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
) -> PaginatedDocumentsResponse:
    return await service.list_documents(
        current_user=current_user,
        page=page,
        page_size=page_size,
        practice_id=practice_id,
        category=category,
        status=status,
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
