from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_priority import TaskPriority
from app.schemas.task_priority import TaskPriorityUpdate


class TaskPriorityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        name: str,
        color: str | None = None,
        sort_order: int | None = None,
        description: str | None = None,
    ) -> TaskPriority:
        priority = TaskPriority(
            name=name, color=color, sort_order=sort_order, description=description
        )
        self.session.add(priority)
        await self.session.flush()
        await self.session.refresh(priority)
        return priority

    async def get_by_id(self, priority_id: str) -> TaskPriority | None:
        result = await self.session.execute(
            select(TaskPriority).where(TaskPriority.id == priority_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> TaskPriority | None:
        result = await self.session.execute(
            select(TaskPriority).where(TaskPriority.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[TaskPriority]:
        result = await self.session.execute(select(TaskPriority).order_by(TaskPriority.name))
        return list(result.scalars().all())

    async def update(self, priority: TaskPriority, payload: TaskPriorityUpdate) -> TaskPriority:
        priority.name = payload.name
        priority.color = payload.color
        priority.sort_order = payload.sort_order
        priority.description = payload.description
        await self.session.flush()
        await self.session.refresh(priority)
        return priority

    async def delete(self, priority: TaskPriority) -> None:
        await self.session.delete(priority)
        await self.session.flush()
