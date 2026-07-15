from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.blc.practice import PracticeService
from app.api.deps import get_practice_service
from app.models.user import User
from app.schemas.practice import PracticeCreate, PracticeRead, PracticeStatusUpdate, PracticeUpdate
from utils.apis_mapping import (
    PRACTICE_CREATE_ROLES,
    PRACTICE_DELETE_ROLES,
    PRACTICE_EDIT_ROLES,
    PRACTICE_READ_ROLES,
    PRACTICE_STATUS_ROLES,
)
from utils.auth_functions import require_roles

router = APIRouter()


@router.post("", response_model=PracticeRead, status_code=status.HTTP_201_CREATED)
async def create_practice(
    payload: PracticeCreate,
    service: Annotated[PracticeService, Depends(get_practice_service)],
    current_user: Annotated[User, Depends(require_roles(PRACTICE_CREATE_ROLES))],
) -> PracticeRead:
    return await service.create_practice(payload, current_user)


@router.get("", response_model=list[PracticeRead])
async def list_practices(
    service: Annotated[PracticeService, Depends(get_practice_service)],
    current_user: Annotated[User, Depends(require_roles(PRACTICE_READ_ROLES))],
    exclude_user_id: Annotated[
        str | None,
        Query(description="Skip practices already assigned to this user."),
    ] = None,
) -> list[PracticeRead]:
    return await service.list_practices(current_user, exclude_user_id=exclude_user_id)


@router.get("/{practice_id}", response_model=PracticeRead)
async def get_practice(
    practice_id: str,
    service: Annotated[PracticeService, Depends(get_practice_service)],
    current_user: Annotated[User, Depends(require_roles(PRACTICE_READ_ROLES))],
) -> PracticeRead:
    return await service.get_practice(practice_id, current_user)


@router.patch("/{practice_id}", response_model=PracticeRead)
async def update_practice(
    practice_id: str,
    payload: PracticeUpdate,
    service: Annotated[PracticeService, Depends(get_practice_service)],
    current_user: Annotated[User, Depends(require_roles(PRACTICE_EDIT_ROLES))],
) -> PracticeRead:
    return await service.update_practice(practice_id, payload, current_user)


@router.patch("/{practice_id}/status", response_model=PracticeRead)
async def update_practice_status(
    practice_id: str,
    payload: PracticeStatusUpdate,
    service: Annotated[PracticeService, Depends(get_practice_service)],
    current_user: Annotated[User, Depends(require_roles(PRACTICE_STATUS_ROLES))],
) -> PracticeRead:
    return await service.update_practice_status(practice_id, payload, current_user)


@router.delete("/{practice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_practice(
    practice_id: str,
    service: Annotated[PracticeService, Depends(get_practice_service)],
    current_user: Annotated[User, Depends(require_roles(PRACTICE_DELETE_ROLES))],
) -> None:
    await service.delete_practice(practice_id, current_user)
