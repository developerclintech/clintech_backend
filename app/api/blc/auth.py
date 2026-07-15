from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.api.blc.otp_delivery import OtpDeliveryService
from app.api.queries.password_reset_otp import PasswordResetOtpRepository
from app.api.queries.user import UserRepository
from app.core.config import Settings
from app.core.security import create_access_token, hash_otp, verify_otp, verify_password
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutMessage,
    PasswordResetMessage,
    ResetPasswordRequest,
    Token,
)

PASSWORD_RESET_REQUESTED_MESSAGE = (
    "If an account exists, a password reset OTP has been sent."
)
PASSWORD_RESET_SUCCESS_MESSAGE = "Password has been reset successfully."
LOGOUT_SUCCESS_MESSAGE = "Logged out successfully."
OTP_DELIVERY_CHANNEL = "email"


class AuthService:
    def __init__(
        self,
        *,
        users: UserRepository,
        password_reset_otps: PasswordResetOtpRepository,
        otp_delivery: OtpDeliveryService,
        settings: Settings,
    ) -> None:
        self.users = users
        self.password_reset_otps = password_reset_otps
        self.otp_delivery = otp_delivery
        self.settings = settings

    async def login(self, payload: LoginRequest) -> Token:
        user = await self.users.get_by_email(payload.email)
        if (
            user is None
            or not user.is_active
            or not verify_password(payload.password, user.hashed_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.required_relogin:
            await self.users.set_required_relogin(user, False)
        access_token = create_access_token(user.id, user.token_version, self.settings)
        return Token(access_token=access_token)

    async def logout(self, user: User) -> LogoutMessage:
        await self.users.increment_token_version(user)
        return LogoutMessage(message=LOGOUT_SUCCESS_MESSAGE)

    async def request_password_reset(
        self,
        payload: ForgotPasswordRequest,
    ) -> PasswordResetMessage:
        user = await self.users.get_by_email(payload.email)
        if user is None or not user.is_active:
            return PasswordResetMessage(message=PASSWORD_RESET_REQUESTED_MESSAGE)

        now = datetime.now(timezone.utc)
        otp_code = self._generate_otp()
        expires_at = now + timedelta(
            minutes=self.settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES
        )

        await self.password_reset_otps.invalidate_active_for_user(user.id, now)
        await self.password_reset_otps.create(
            user_id=user.id,
            delivery_channel=OTP_DELIVERY_CHANNEL,
            destination=user.email,
            otp_hash=hash_otp(otp_code, self.settings),
            expires_at=expires_at,
        )
        try:
            await self.otp_delivery.send_password_reset_otp(
                destination=user.email,
                otp_code=otp_code,
                expires_at=expires_at,
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send password reset email. Please try again later.",
            ) from exc

        return PasswordResetMessage(message=PASSWORD_RESET_REQUESTED_MESSAGE)

    async def reset_password(
        self,
        payload: ResetPasswordRequest,
    ) -> PasswordResetMessage:
        user = await self.users.get_by_email(payload.email)
        if user is None or not user.is_active:
            raise self._invalid_otp_error()

        now = datetime.now(timezone.utc)
        otp = await self.password_reset_otps.get_latest_active(
            user_id=user.id,
            delivery_channel=OTP_DELIVERY_CHANNEL,
            now=now,
        )
        if otp is None or otp.attempts >= self.settings.PASSWORD_RESET_OTP_MAX_ATTEMPTS:
            raise self._invalid_otp_error()

        await self.password_reset_otps.increment_attempts(otp)
        if not verify_otp(payload.otp_code, otp.otp_hash, self.settings):
            if otp.attempts >= self.settings.PASSWORD_RESET_OTP_MAX_ATTEMPTS:
                await self.password_reset_otps.consume(otp, now)
            raise self._invalid_otp_error()

        await self.users.update_password(user, payload.new_password)
        await self.users.increment_token_version(user)
        await self.password_reset_otps.consume(otp, now)
        return PasswordResetMessage(message=PASSWORD_RESET_SUCCESS_MESSAGE)

    def _generate_otp(self) -> str:
        max_value = 10**self.settings.PASSWORD_RESET_OTP_LENGTH
        return f"{secrets.randbelow(max_value):0{self.settings.PASSWORD_RESET_OTP_LENGTH}d}"

    @staticmethod
    def _invalid_otp_error() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP.",
        )
