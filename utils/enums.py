from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    PRACTICE_ADMIN = "practice_admin"
    CODER = "coder"
    RECEPTIONIST = "receptionist"
    STAFF = "staff"
