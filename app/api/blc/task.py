from __future__ import annotations

import math

from fastapi import HTTPException, status

from app.api.queries.document import DocumentRepository
from app.api.queries.task import TaskRepository
from app.api.queries.task_category import TaskCategoryRepository
from app.api.queries.task_priority import TaskPriorityRepository
from app.api.queries.user import UserRepository
from app.models.user import User
from app.schemas.task import (
    PaginatedTasksResponse,
    TaskAssign,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from utils.enums import TaskStatus


def _to_read(task: object) -> TaskRead:
    read = TaskRead.model_validate(task)
    if task.created_by:
        read.created_by_name = task.created_by.full_name
    if task.assigned_to:
        read.assigned_to_name = task.assigned_to.full_name
    if task.document:
        read.document_filename = task.document.filename
    return read


class TaskService:
    def __init__(
        self,
        *,
        tasks: TaskRepository,
        users: UserRepository,
        task_categories: TaskCategoryRepository,
        task_priorities: TaskPriorityRepository,
        documents: DocumentRepository,
    ) -> None:
        self.tasks = tasks
        self.users = users
        self.task_categories = task_categories
        self.task_priorities = task_priorities
        self.documents = documents

    async def _validate_assignee(self, assigned_to_id: str | None) -> None:
        if assigned_to_id is not None:
            user = await self.users.get_by_id(assigned_to_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assigned user not found.",
                )

    async def _validate_document(self, document_id: str | None) -> None:
        if document_id is not None:
            document = await self.documents.get_by_id(document_id)
            if document is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found.",
                )

    async def _validate_priority(self, priority: str) -> None:
        found = await self.task_priorities.get_by_name(priority)
        if found is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Priority '{priority}' is not defined.",
            )

    async def _validate_category(self, category: str) -> None:
        found = await self.task_categories.get_by_name(category)
        if found is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category}' is not defined.",
            )

    async def create_task(self, payload: TaskCreate, current_user: User) -> TaskRead:
        await self._validate_assignee(payload.assigned_to_id)
        await self._validate_priority(payload.priority)
        await self._validate_category(payload.category)
        await self._validate_document(payload.document_id)
        task = await self.tasks.create(
            title=payload.title,
            priority=payload.priority,
            category=payload.category,
            description=payload.description,
            created_by_id=current_user.id,
            assigned_to_id=payload.assigned_to_id,
            practice_id=payload.practice_id,
            document_id=payload.document_id,
        )
        task = await self.tasks.get_by_id(task.id)
        return _to_read(task)

    async def list_tasks(
        self,
        current_user: User,
        page: int,
        page_size: int,
        status: TaskStatus | None = None,
        priority: str | None = None,
        category: str | None = None,
        practice_id: str | None = None,
        assigned_to_id: str | None = None,
        document_id: str | None = None,
    ) -> PaginatedTasksResponse:
        tasks, total = await self.tasks.get_paginated(
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            category=category,
            practice_id=practice_id,
            assigned_to_id=assigned_to_id,
            document_id=document_id,
        )
        items = [_to_read(t) for t in tasks]
        return PaginatedTasksResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if page_size else 0,
        )

    async def get_task(self, task_id: str, current_user: User) -> TaskRead:
        task = await self.tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        return _to_read(task)

    async def update_task(
        self, task_id: str, payload: TaskUpdate, current_user: User
    ) -> TaskRead:
        task = await self.tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        if payload.priority is not None:
            await self._validate_priority(payload.priority)
        if payload.category is not None:
            await self._validate_category(payload.category)
        if payload.document_id is not None:
            await self._validate_document(payload.document_id)
        task = await self.tasks.update(task, payload)
        task = await self.tasks.get_by_id(task.id)
        return _to_read(task)

    async def assign_task(
        self, task_id: str, payload: TaskAssign, current_user: User
    ) -> TaskRead:
        task = await self.tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        await self._validate_assignee(payload.assigned_to_id)
        task = await self.tasks.assign(task, payload)
        task = await self.tasks.get_by_id(task.id)
        return _to_read(task)

    async def update_task_status(
        self, task_id: str, new_status: TaskStatus, current_user: User
    ) -> TaskRead:
        task = await self.tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        task = await self.tasks.update_status(task, new_status)
        task = await self.tasks.get_by_id(task.id)
        return _to_read(task)

    async def update_task_priority(
        self, task_id: str, priority: str, current_user: User
    ) -> TaskRead:
        task = await self.tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        await self._validate_priority(priority)
        task = await self.tasks.update_priority(task, priority)
        task = await self.tasks.get_by_id(task.id)
        return _to_read(task)

    async def update_task_category(
        self, task_id: str, category: str, current_user: User
    ) -> TaskRead:
        task = await self.tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        await self._validate_category(category)
        task = await self.tasks.update_category(task, category)
        task = await self.tasks.get_by_id(task.id)
        return _to_read(task)

    async def delete_task(self, task_id: str, current_user: User) -> None:
        task = await self.tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        await self.tasks.delete(task)
