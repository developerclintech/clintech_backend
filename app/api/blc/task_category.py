from __future__ import annotations

from fastapi import HTTPException, status

from app.api.queries.practice import PracticeRepository
from app.api.queries.task_category import TaskCategoryRepository
from app.models.user import User
from app.schemas.task_category import TaskCategoryCreate, TaskCategoryRead, TaskCategoryUpdate


class TaskCategoryService:
    def __init__(self, *, categories: TaskCategoryRepository, practices: PracticeRepository) -> None:
        self.categories = categories
        self.practices = practices

    async def _ensure_practice_exists(self, practice_id: str) -> None:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )

    async def _ensure_name_available(self, practice_id: str, name: str) -> None:
        existing = await self.categories.get_by_name(practice_id, name)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A category with this name already exists for this practice.",
            )

    async def create_category(
        self, payload: TaskCategoryCreate, current_user: User
    ) -> TaskCategoryRead:
        await self._ensure_practice_exists(payload.practice_id)
        await self._ensure_name_available(payload.practice_id, payload.name)
        category = await self.categories.create(name=payload.name, practice_id=payload.practice_id)
        return TaskCategoryRead.model_validate(category)

    async def list_categories(
        self, practice_id: str | None, current_user: User
    ) -> list[TaskCategoryRead]:
        categories = await self.categories.get_all(practice_id)
        return [TaskCategoryRead.model_validate(c) for c in categories]

    async def get_category(self, category_id: str, current_user: User) -> TaskCategoryRead:
        category = await self.categories.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        return TaskCategoryRead.model_validate(category)

    async def update_category(
        self, category_id: str, payload: TaskCategoryUpdate, current_user: User
    ) -> TaskCategoryRead:
        category = await self.categories.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        if payload.name != category.name:
            await self._ensure_name_available(category.practice_id, payload.name)
        category = await self.categories.update(category, payload)
        return TaskCategoryRead.model_validate(category)

    async def delete_category(self, category_id: str, current_user: User) -> None:
        category = await self.categories.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        await self.categories.delete(category)
