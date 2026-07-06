from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskAssign, TaskUpdate
from utils.enums import TaskStatus


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        title: str,
        priority: str,
        category: str,
        description: str,
        created_by_id: str,
        assigned_to_id: str | None = None,
        practice_id: str | None = None,
    ) -> Task:
        task = Task(
            title=title,
            priority=priority,
            category=category,
            description=description,
            status=TaskStatus.PENDING.value,
            created_by_id=created_by_id,
            assigned_to_id=assigned_to_id,
            practice_id=practice_id,
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: str) -> Task | None:
        result = await self.session.execute(
            select(Task)
            .options(
                joinedload(Task.created_by),
                joinedload(Task.assigned_to),
                joinedload(Task.practice),
            )
            .where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def update(self, task: Task, payload: TaskUpdate) -> Task:
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(task, field, value)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def assign(self, task: Task, payload: TaskAssign) -> Task:
        task.assigned_to_id = payload.assigned_to_id
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def update_status(self, task: Task, new_status: TaskStatus) -> Task:
        task.status = new_status.value
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def update_priority(self, task: Task, priority: str) -> Task:
        task.priority = priority
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def update_category(self, task: Task, category: str) -> Task:
        task.category = category
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.flush()

    async def get_paginated(
        self,
        *,
        page: int,
        page_size: int,
        status: TaskStatus | None = None,
        priority: str | None = None,
        category: str | None = None,
        practice_id: str | None = None,
        assigned_to_id: str | None = None,
    ) -> tuple[list[Task], int]:
        base = select(Task).options(
            joinedload(Task.created_by),
            joinedload(Task.assigned_to),
            joinedload(Task.practice),
        )
        count_base = select(func.count()).select_from(Task)

        if status is not None:
            base = base.where(Task.status == status.value)
            count_base = count_base.where(Task.status == status.value)
        if priority is not None:
            base = base.where(Task.priority == priority)
            count_base = count_base.where(Task.priority == priority)
        if category is not None:
            base = base.where(Task.category == category)
            count_base = count_base.where(Task.category == category)
        if practice_id is not None:
            base = base.where(Task.practice_id == practice_id)
            count_base = count_base.where(Task.practice_id == practice_id)
        if assigned_to_id is not None:
            base = base.where(Task.assigned_to_id == assigned_to_id)
            count_base = count_base.where(Task.assigned_to_id == assigned_to_id)

        total = (await self.session.execute(count_base)).scalar_one()

        offset = (page - 1) * page_size
        rows = await self.session.execute(
            base.order_by(Task.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(rows.scalars().unique().all()), total
