from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.blc.auth import AuthService
from app.api.deps import get_auth_service
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutMessage,
    PasswordResetMessage,
    ResetPasswordRequest,
    Token,
)
from utils.auth_functions import get_current_user

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    return await service.login(payload)


@router.post("/logout", response_model=LogoutMessage)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> LogoutMessage:
    return await service.logout(current_user)


@router.post("/forgot-password", response_model=PasswordResetMessage)
async def forgot_password(
    payload: ForgotPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> PasswordResetMessage:
    return await service.request_password_reset(payload)


@router.post("/reset-password", response_model=PasswordResetMessage)
async def reset_password(
    payload: ResetPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> PasswordResetMessage:
    return await service.reset_password(payload)
