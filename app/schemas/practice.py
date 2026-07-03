from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PracticeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    ods_code: str | None = Field(default=None, min_length=1, max_length=20)
    notice: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    website: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=500)
    practice_hours: dict[str, Any] | None = None
    is_emis_enabled: bool | None = None


class PracticeStatusUpdate(BaseModel):
    is_active: bool


class PracticeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    ods_code: str = Field(min_length=1, max_length=20)
    notice: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    website: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=500)
    practice_hours: dict[str, Any] | None = None
    is_emis_enabled: bool = False


class PracticeRead(BaseModel):
    id: str
    name: str
    ods_code: str
    notice: str | None
    phone: str | None
    website: str | None
    email: str | None
    address: str | None
    practice_hours: dict[str, Any] | None
    is_emis_enabled: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
