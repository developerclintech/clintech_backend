from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.blc.task_category import TaskCategoryService
from app.api.deps import get_task_category_service
from app.models.user import User
from app.schemas.task_category import TaskCategoryCreate, TaskCategoryRead, TaskCategoryUpdate
from utils.apis_mapping import TASK_CATEGORY_MANAGE_ROLES, TASK_CATEGORY_READ_ROLES
from utils.auth_functions import require_roles

router = APIRouter()


@router.post(
    "",
    response_model=TaskCategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task category",
)
async def create_task_category(
    payload: TaskCategoryCreate,
    service: Annotated[TaskCategoryService, Depends(get_task_category_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_CATEGORY_MANAGE_ROLES))],
) -> TaskCategoryRead:
    return await service.create_category(payload, current_user)


@router.get(
    "",
    response_model=list[TaskCategoryRead],
    summary="List task categories",
)
async def list_task_categories(
    service: Annotated[TaskCategoryService, Depends(get_task_category_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_CATEGORY_READ_ROLES))],
    practice_id: Annotated[str | None, Query()] = None,
) -> list[TaskCategoryRead]:
    return await service.list_categories(practice_id, current_user)


@router.get(
    "/{category_id}",
    response_model=TaskCategoryRead,
    summary="Get task category details",
)
async def get_task_category(
    category_id: str,
    service: Annotated[TaskCategoryService, Depends(get_task_category_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_CATEGORY_READ_ROLES))],
) -> TaskCategoryRead:
    return await service.get_category(category_id, current_user)


@router.patch(
    "/{category_id}",
    response_model=TaskCategoryRead,
    summary="Rename a task category",
)
async def update_task_category(
    category_id: str,
    payload: TaskCategoryUpdate,
    service: Annotated[TaskCategoryService, Depends(get_task_category_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_CATEGORY_MANAGE_ROLES))],
) -> TaskCategoryRead:
    return await service.update_category(category_id, payload, current_user)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task category",
)
async def delete_task_category(
    category_id: str,
    service: Annotated[TaskCategoryService, Depends(get_task_category_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_CATEGORY_MANAGE_ROLES))],
) -> None:
    await service.delete_category(category_id, current_user)
