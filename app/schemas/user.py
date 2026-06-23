from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from utils.enums import UserRole


class RoleAssignment(BaseModel):
    practice_id: str = Field(min_length=1)
    role: UserRole

    @field_validator("role")
    @classmethod
    def role_not_super_admin(cls, v: UserRole) -> UserRole:
        if v == UserRole.SUPER_ADMIN:
            raise ValueError("super_admin cannot be assigned via user creation.")
        return v


class UserCreate(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=255)
    middle_name: str | None = Field(default=None, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    roles: list[RoleAssignment] = Field(min_length=1)

    @field_validator("roles")
    @classmethod
    def roles_unique(cls, v: list[RoleAssignment]) -> list[RoleAssignment]:
        seen = {(assignment.practice_id, assignment.role) for assignment in v}
        if len(seen) != len(v):
            raise ValueError("Duplicate practice/role assignments are not allowed.")
        return v


class MembershipCreate(BaseModel):
    practice_id: str | None = None
    role: UserRole


class MembershipRead(BaseModel):
    id: str
    user_id: str
    practice_id: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: str
    email: str
    first_name: str
    middle_name: str | None
    last_name: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    memberships: list[MembershipRead] = Field(default=[], alias="practice_memberships")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
