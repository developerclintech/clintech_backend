from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.db_session import get_db
from app.core.security import decode_access_token
from app.models.user import User
from utils.enums import UserRole

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(_oauth2_scheme)],
    session: DbSessionDep,
    settings: SettingsDep,
) -> User:
    from app.api.queries.user import UserRepository

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id, token_version = decode_access_token(token, settings)
    except jwt.JWTError:
        raise credentials_error

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_error
    if user.token_version != token_version or user.required_relogin:
        raise credentials_error
    return user


def _role_value(role: UserRole | str) -> str:
    return role.value if isinstance(role, UserRole) else role


def _active_memberships(current_user: User):
    return (
        membership
        for membership in current_user.practice_memberships
        if membership.is_active
    )


def is_super_admin(current_user: User) -> bool:
    return any(
        membership.practice_id is None
        and _role_value(membership.role) == UserRole.SUPER_ADMIN.value
        for membership in _active_memberships(current_user)
    )


def has_role(
    current_user: User,
    allowed: list[UserRole | str],
    *,
    practice_id: str | None = None,
) -> bool:
    if is_super_admin(current_user):
        return True

    allowed_values = {_role_value(role) for role in allowed}
    practice_id_value = str(practice_id) if practice_id is not None else None

    return any(
        _role_value(membership.role) in allowed_values
        and (
            practice_id_value is None
            or membership.practice_id == practice_id_value
        )
        for membership in _active_memberships(current_user)
    )


def require_roles(allowed: list[UserRole | str]) -> Callable:
    async def _check(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if not has_role(current_user, allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your role is not allowed to perform this action.",
            )
        return current_user

    return _check


def require_practice_roles(
    allowed: list[UserRole | str],
    *,
    practice_id_param: str = "practice_id",
) -> Callable:
    async def _check(
        request: Request,
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        practice_id = request.path_params.get(practice_id_param) or request.query_params.get(
            practice_id_param
        )
        if practice_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing practice scope '{practice_id_param}'.",
            )

        if not has_role(current_user, allowed, practice_id=str(practice_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your role is not allowed for this practice.",
            )
        return current_user

    return _check


def check_practice_access(entity_practice_id: str | None, current_user: User) -> None:
    if is_super_admin(current_user):
        return

    if entity_practice_id is None or not has_role(
        current_user,
        [
            UserRole.PRACTICE_ADMIN,
            UserRole.CODER,
            UserRole.RECEPTIONIST,
            UserRole.STAFF,
        ],
        practice_id=entity_practice_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this practice's data.",
        )
