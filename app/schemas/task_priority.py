from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskPriorityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    practice_id: str


class TaskPriorityUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=20)


class TaskPriorityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    practice_id: str
    created_at: datetime
    updated_at: datetime
