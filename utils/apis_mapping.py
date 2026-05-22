from __future__ import annotations

from utils.enums import UserRole

USER_CREATE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]

USER_READ_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]

MEMBERSHIP_MANAGE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]

PRACTICE_CREATE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
]

PRACTICE_READ_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]

PRACTICE_EDIT_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]

PRACTICE_DELETE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
]

PRACTICE_STATUS_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
]
