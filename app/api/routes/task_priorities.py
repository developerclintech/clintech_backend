from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.blc.task_priority import TaskPriorityService
from app.api.deps import get_task_priority_service
from app.models.user import User
from app.schemas.task_priority import TaskPriorityCreate, TaskPriorityRead, TaskPriorityUpdate
from utils.apis_mapping import TASK_PRIORITY_MANAGE_ROLES, TASK_PRIORITY_READ_ROLES
from utils.auth_functions import require_roles

router = APIRouter()


@router.post(
    "",
    response_model=TaskPriorityRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task priority",
)
async def create_task_priority(
    payload: TaskPriorityCreate,
    service: Annotated[TaskPriorityService, Depends(get_task_priority_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_PRIORITY_MANAGE_ROLES))],
) -> TaskPriorityRead:
    return await service.create_priority(payload, current_user)


@router.get(
    "",
    response_model=list[TaskPriorityRead],
    summary="List task priorities",
)
async def list_task_priorities(
    service: Annotated[TaskPriorityService, Depends(get_task_priority_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_PRIORITY_MANAGE_ROLES))],
) -> list[TaskPriorityRead]:
    return await service.list_priorities(current_user)


@router.get(
    "/{priority_id}",
    response_model=TaskPriorityRead,
    summary="Get task priority details",
)
async def get_task_priority(
    priority_id: str,
    service: Annotated[TaskPriorityService, Depends(get_task_priority_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_PRIORITY_READ_ROLES))],
) -> TaskPriorityRead:
    return await service.get_priority(priority_id, current_user)


@router.patch(
    "/{priority_id}",
    response_model=TaskPriorityRead,
    summary="Rename a task priority",
)
async def update_task_priority(
    priority_id: str,
    payload: TaskPriorityUpdate,
    service: Annotated[TaskPriorityService, Depends(get_task_priority_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_PRIORITY_MANAGE_ROLES))],
) -> TaskPriorityRead:
    return await service.update_priority(priority_id, payload, current_user)


@router.delete(
    "/{priority_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task priority",
)
async def delete_task_priority(
    priority_id: str,
    service: Annotated[TaskPriorityService, Depends(get_task_priority_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_PRIORITY_MANAGE_ROLES))],
) -> None:
    await service.delete_priority(priority_id, current_user)
