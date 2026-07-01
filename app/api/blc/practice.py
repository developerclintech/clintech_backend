from __future__ import annotations

from fastapi import HTTPException, status

from app.api.queries.practice import PracticeRepository
from app.api.queries.task_category import TaskCategoryRepository
from app.api.queries.task_priority import TaskPriorityRepository
from app.models.user import User
from app.schemas.practice import PracticeCreate, PracticeRead, PracticeStatusUpdate, PracticeUpdate
from utils.enums import DEFAULT_TASK_CATEGORIES, DEFAULT_TASK_PRIORITIES


class PracticeService:
    def __init__(
        self,
        *,
        practices: PracticeRepository,
        task_categories: TaskCategoryRepository,
        task_priorities: TaskPriorityRepository,
    ) -> None:
        self.practices = practices
        self.task_categories = task_categories
        self.task_priorities = task_priorities

    async def create_practice(
        self, payload: PracticeCreate, current_user: User
    ) -> PracticeRead:
        practice = await self.practices.create(payload)
        for name in DEFAULT_TASK_CATEGORIES:
            await self.task_categories.create(name=name, practice_id=practice.id)
        for name in DEFAULT_TASK_PRIORITIES:
            await self.task_priorities.create(name=name, practice_id=practice.id)
        return PracticeRead.model_validate(practice)

    async def get_practice(
        self, practice_id: str, current_user: User
    ) -> PracticeRead:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )
        return PracticeRead.model_validate(practice)

    async def list_practices(self, current_user: User) -> list[PracticeRead]:
        practices = await self.practices.get_all()
        return [PracticeRead.model_validate(p) for p in practices]

    async def update_practice(
        self, practice_id: str, payload: PracticeUpdate, current_user: User
    ) -> PracticeRead:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )
        practice = await self.practices.update(practice, payload)
        return PracticeRead.model_validate(practice)

    async def update_practice_status(
        self, practice_id: str, payload: PracticeStatusUpdate, current_user: User
    ) -> PracticeRead:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )
        practice = await self.practices.set_status(practice, payload.is_active)
        return PracticeRead.model_validate(practice)

    async def delete_practice(self, practice_id: str, current_user: User) -> None:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )
        await self.practices.delete(practice)
