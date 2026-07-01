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

DOCUMENT_UPLOAD_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

DOCUMENT_READ_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

DOCUMENT_EDIT_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

DOCUMENT_DELETE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]

TASK_CREATE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

TASK_READ_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

TASK_EDIT_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

TASK_ASSIGN_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

TASK_DELETE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]

TASK_CATEGORY_READ_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

TASK_CATEGORY_MANAGE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]

TASK_PRIORITY_READ_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
    UserRole.CODER,
    UserRole.RECEPTIONIST,
    UserRole.STAFF,
]

TASK_PRIORITY_MANAGE_ROLES: list[UserRole] = [
    UserRole.SUPER_ADMIN,
    UserRole.PRACTICE_ADMIN,
]
