from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskPriorityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    color: str | None = Field(default=None, max_length=7)
    sort_order: int | None = None
    description: str | None = None


class TaskPriorityUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    color: str | None = Field(default=None, max_length=7)
    sort_order: int | None = None
    description: str | None = None


class TaskPriorityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    color: str | None
    sort_order: int | None
    description: str | None
    created_at: datetime
    updated_at: datetime
