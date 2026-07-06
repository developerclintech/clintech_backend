from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_category import TaskCategory
from app.schemas.task_category import TaskCategoryUpdate


class TaskCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, *, name: str, color: str | None = None, description: str | None = None
    ) -> TaskCategory:
        category = TaskCategory(name=name, color=color, description=description)
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def get_by_id(self, category_id: str) -> TaskCategory | None:
        result = await self.session.execute(
            select(TaskCategory).where(TaskCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> TaskCategory | None:
        result = await self.session.execute(
            select(TaskCategory).where(TaskCategory.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[TaskCategory]:
        result = await self.session.execute(select(TaskCategory).order_by(TaskCategory.name))
        return list(result.scalars().all())

    async def update(self, category: TaskCategory, payload: TaskCategoryUpdate) -> TaskCategory:
        category.name = payload.name
        category.color = payload.color
        category.description = payload.description
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category: TaskCategory) -> None:
        await self.session.delete(category)
        await self.session.flush()
