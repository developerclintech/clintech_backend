from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    practice_id: str
    color: str | None = Field(default=None, max_length=7)
    description: str | None = None


class TaskCategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str | None = Field(default=None, max_length=7)
    description: str | None = None


class TaskCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    color: str | None
    description: str | None
    practice_id: str
    created_at: datetime
    updated_at: datetime
