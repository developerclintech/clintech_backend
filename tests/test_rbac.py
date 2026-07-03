from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.models.user import User
from app.models.user_practice import UserPractice
from utils.auth_functions import check_practice_access, has_role, is_super_admin
from utils.enums import UserRole


def make_user(*memberships: UserPractice) -> User:
    return User(
        id="user-1",
        email="user@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_active=True,
        practice_memberships=list(memberships),
    )


def make_membership(practice_id: str | None, role: UserRole) -> UserPractice:
    return UserPractice(
        id=f"membership-{practice_id or 'global'}-{role.value}",
        user_id="user-1",
        practice_id=practice_id,
        role=role,
        is_active=True,
    )


def test_user_can_have_same_role_across_multiple_practices() -> None:
    user = make_user(
        make_membership("practice-1", UserRole.CODER),
        make_membership("practice-2", UserRole.CODER),
    )

    assert has_role(user, [UserRole.CODER], practice_id="practice-1")
    assert has_role(user, [UserRole.CODER], practice_id="practice-2")


def test_user_can_have_different_roles_per_practice() -> None:
    user = make_user(
        make_membership("practice-1", UserRole.RECEPTIONIST),
        make_membership("practice-2", UserRole.PRACTICE_ADMIN),
    )

    assert has_role(user, [UserRole.RECEPTIONIST], practice_id="practice-1")
    assert has_role(user, [UserRole.PRACTICE_ADMIN], practice_id="practice-2")
    assert not has_role(user, [UserRole.PRACTICE_ADMIN], practice_id="practice-1")


def test_user_can_have_multiple_roles_in_same_practice() -> None:
    user = make_user(
        make_membership("practice-1", UserRole.CODER),
        make_membership("practice-1", UserRole.RECEPTIONIST),
    )

    assert has_role(user, [UserRole.CODER], practice_id="practice-1")
    assert has_role(user, [UserRole.RECEPTIONIST], practice_id="practice-1")
    assert has_role(
        user,
        [UserRole.PRACTICE_ADMIN, UserRole.CODER],
        practice_id="practice-1",
    )


def test_super_admin_global_membership_can_access_any_practice() -> None:
    user = make_user(make_membership(None, UserRole.SUPER_ADMIN))

    assert is_super_admin(user)
    check_practice_access("practice-999", user)


def test_unassigned_practice_access_is_forbidden() -> None:
    user = make_user(make_membership("practice-1", UserRole.CODER))

    with pytest.raises(HTTPException) as exc_info:
        check_practice_access("practice-2", user)

    assert exc_info.value.status_code == 403
