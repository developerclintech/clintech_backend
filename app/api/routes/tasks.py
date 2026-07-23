from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.blc.task import TaskService
from app.api.deps import get_task_service
from app.models.user import User
from app.schemas.task import (
    PaginatedTasksResponse,
    TaskAssign,
    TaskCategoryChange,
    TaskCreate,
    TaskPriorityChange,
    TaskRead,
    TaskStatusUpdate,
    TaskUpdate,
)
from utils.apis_mapping import (
    TASK_ASSIGN_ROLES,
    TASK_CREATE_ROLES,
    TASK_DELETE_ROLES,
    TASK_EDIT_ROLES,
    TASK_READ_ROLES,
)
from utils.auth_functions import require_roles
from utils.enums import TaskStatus

router = APIRouter()


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    payload: TaskCreate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_CREATE_ROLES))],
) -> TaskRead:
    return await service.create_task(payload, current_user)


@router.get(
    "",
    response_model=PaginatedTasksResponse,
    summary="List tasks with filtering and pagination",
)
async def list_tasks(
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_READ_ROLES))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: Annotated[TaskStatus | None, Query()] = None,
    priority: Annotated[str | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
    practice_id: Annotated[str | None, Query()] = None,
    assigned_to_id: Annotated[str | None, Query()] = None,
    document_id: Annotated[str | None, Query()] = None,
) -> PaginatedTasksResponse:
    return await service.list_tasks(
        current_user=current_user,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        category=category,
        practice_id=practice_id,
        assigned_to_id=assigned_to_id,
        document_id=document_id,
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get task details",
)
async def get_task(
    task_id: str,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_READ_ROLES))],
) -> TaskRead:
    return await service.get_task(task_id, current_user)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update task information",
)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_EDIT_ROLES))],
) -> TaskRead:
    return await service.update_task(task_id, payload, current_user)


@router.patch(
    "/{task_id}/assign",
    response_model=TaskRead,
    summary="Assign or reassign a task to a staff member",
)
async def assign_task(
    task_id: str,
    payload: TaskAssign,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_ASSIGN_ROLES))],
) -> TaskRead:
    return await service.assign_task(task_id, payload, current_user)


@router.patch(
    "/{task_id}/status",
    response_model=TaskRead,
    summary="Update task status",
)
async def update_task_status(
    task_id: str,
    payload: TaskStatusUpdate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_EDIT_ROLES))],
) -> TaskRead:
    return await service.update_task_status(task_id, payload.status, current_user)


@router.patch(
    "/{task_id}/priority",
    response_model=TaskRead,
    summary="Change task priority",
)
async def update_task_priority(
    task_id: str,
    payload: TaskPriorityChange,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_EDIT_ROLES))],
) -> TaskRead:
    return await service.update_task_priority(task_id, payload.priority, current_user)


@router.patch(
    "/{task_id}/category",
    response_model=TaskRead,
    summary="Change task category",
)
async def update_task_category(
    task_id: str,
    payload: TaskCategoryChange,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_EDIT_ROLES))],
) -> TaskRead:
    return await service.update_task_category(task_id, payload.category, current_user)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: str,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(require_roles(TASK_DELETE_ROLES))],
) -> None:
    await service.delete_task(task_id, current_user)
