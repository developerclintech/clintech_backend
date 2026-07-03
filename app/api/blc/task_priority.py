from __future__ import annotations

from fastapi import HTTPException, status

from app.api.queries.practice import PracticeRepository
from app.api.queries.task_priority import TaskPriorityRepository
from app.models.user import User
from app.schemas.task_priority import TaskPriorityCreate, TaskPriorityRead, TaskPriorityUpdate


class TaskPriorityService:
    def __init__(self, *, priorities: TaskPriorityRepository, practices: PracticeRepository) -> None:
        self.priorities = priorities
        self.practices = practices

    async def _ensure_practice_exists(self, practice_id: str) -> None:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )

    async def _ensure_name_available(self, practice_id: str, name: str) -> None:
        existing = await self.priorities.get_by_name(practice_id, name)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A priority with this name already exists for this practice.",
            )

    async def create_priority(
        self, payload: TaskPriorityCreate, current_user: User
    ) -> TaskPriorityRead:
        await self._ensure_practice_exists(payload.practice_id)
        await self._ensure_name_available(payload.practice_id, payload.name)
        priority = await self.priorities.create(name=payload.name, practice_id=payload.practice_id)
        return TaskPriorityRead.model_validate(priority)

    async def list_priorities(
        self, practice_id: str | None, current_user: User
    ) -> list[TaskPriorityRead]:
        priorities = await self.priorities.get_all(practice_id)
        return [TaskPriorityRead.model_validate(p) for p in priorities]

    async def get_priority(self, priority_id: str, current_user: User) -> TaskPriorityRead:
        priority = await self.priorities.get_by_id(priority_id)
        if priority is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Priority not found.",
            )
        return TaskPriorityRead.model_validate(priority)

    async def update_priority(
        self, priority_id: str, payload: TaskPriorityUpdate, current_user: User
    ) -> TaskPriorityRead:
        priority = await self.priorities.get_by_id(priority_id)
        if priority is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Priority not found.",
            )
        if payload.name != priority.name:
            await self._ensure_name_available(priority.practice_id, payload.name)
        priority = await self.priorities.update(priority, payload)
        return TaskPriorityRead.model_validate(priority)

    async def delete_priority(self, priority_id: str, current_user: User) -> None:
        priority = await self.priorities.get_by_id(priority_id)
        if priority is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Priority not found.",
            )
        await self.priorities.delete(priority)
