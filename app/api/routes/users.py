from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.blc.user import UserService
from app.api.deps import get_user_service
from app.models.user import User
from app.schemas.user import MembershipCreate, MembershipRead, UserCreate, UserRead, UserStatusUpdate, UserUpdate
from utils.apis_mapping import (
    MEMBERSHIP_DELETE_ROLES,
    MEMBERSHIP_MANAGE_ROLES,
    USER_CREATE_ROLES,
    USER_DELETE_ROLES,
    USER_EDIT_ROLES,
    USER_READ_ROLES,
    USER_STATUS_ROLES,
)
from utils.auth_functions import require_roles

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_roles(USER_CREATE_ROLES))],
) -> UserRead:
    return await service.create_user(payload, current_user)


@router.get("", response_model=list[UserRead])
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_roles(USER_READ_ROLES))],
) -> list[UserRead]:
    return await service.list_users(current_user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_roles(USER_READ_ROLES))],
) -> UserRead:
    return await service.get_user(user_id, current_user)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_roles(USER_EDIT_ROLES))],
) -> UserRead:
    return await service.update_user(user_id, payload, current_user)


@router.patch("/{user_id}/status", response_model=UserRead)
async def update_user_status(
    user_id: str,
    payload: UserStatusUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_roles(USER_STATUS_ROLES))],
) -> UserRead:
    return await service.update_user_status(user_id, payload, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_roles(USER_DELETE_ROLES))],
) -> None:
    await service.delete_user(user_id, current_user)


@router.post(
    "/{user_id}/memberships",
    response_model=MembershipRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_membership(
    user_id: str,
    payload: MembershipCreate,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_roles(MEMBERSHIP_MANAGE_ROLES))],
) -> MembershipRead:
    return await service.add_membership(user_id, payload, current_user)


@router.delete(
    "/{user_id}/memberships/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_membership(
    user_id: str,
    membership_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_roles(MEMBERSHIP_DELETE_ROLES))],
) -> None:
    await service.remove_membership(user_id, membership_id, current_user)
