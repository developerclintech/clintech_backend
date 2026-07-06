from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from utils.enums import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    priority: str = Field(min_length=1, max_length=20)
    category: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=2000)
    assigned_to_id: str | None = None
    practice_id: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    priority: str | None = Field(default=None, min_length=1, max_length=20)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, min_length=1, max_length=2000)


class TaskAssign(BaseModel):
    assigned_to_id: str | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskPriorityChange(BaseModel):
    priority: str = Field(min_length=1, max_length=20)


class TaskCategoryChange(BaseModel):
    category: str = Field(min_length=1, max_length=50)


class AssignedUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    priority: str
    category: str
    description: str
    status: TaskStatus
    created_by_id: str
    created_by_name: str | None = None
    assigned_to_id: str | None
    assigned_to_name: str | None = None
    practice_id: str | None
    created_at: datetime
    updated_at: datetime


class PaginatedTasksResponse(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    page_size: int
    pages: int
