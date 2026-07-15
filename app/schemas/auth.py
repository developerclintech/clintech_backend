from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)


class ResetPasswordRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    otp_code: str = Field(min_length=4, max_length=12)
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetMessage(BaseModel):
    message: str


class LogoutMessage(BaseModel):
    message: str
