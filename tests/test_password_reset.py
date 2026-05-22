from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.blc.auth import AuthService
from app.core.config import Settings
from app.core.security import verify_password
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest


class FakeUserRepository:
    def __init__(self, user: SimpleNamespace | None) -> None:
        self.user = user

    async def get_by_email(self, email: str) -> SimpleNamespace | None:
        if self.user is not None and self.user.email == email:
            return self.user
        return None

    async def update_password(self, user: SimpleNamespace, password: str) -> SimpleNamespace:
        from app.core.security import hash_password

        user.hashed_password = hash_password(password)
        return user


class FakePasswordResetOtpRepository:
    def __init__(self) -> None:
        self.otps: list[SimpleNamespace] = []

    async def invalidate_active_for_user(self, user_id: str, now: datetime) -> None:
        for otp in self.otps:
            if otp.user_id == user_id and otp.consumed_at is None:
                otp.consumed_at = now

    async def create(
        self,
        *,
        user_id: str,
        delivery_channel: str,
        destination: str,
        otp_hash: str,
        expires_at: datetime,
    ) -> SimpleNamespace:
        otp = SimpleNamespace(
            user_id=user_id,
            delivery_channel=delivery_channel,
            destination=destination,
            otp_hash=otp_hash,
            expires_at=expires_at,
            consumed_at=None,
            attempts=0,
        )
        self.otps.append(otp)
        return otp

    async def get_latest_active(
        self,
        *,
        user_id: str,
        delivery_channel: str,
        now: datetime,
    ) -> SimpleNamespace | None:
        active = [
            otp
            for otp in self.otps
            if otp.user_id == user_id
            and otp.delivery_channel == delivery_channel
            and otp.consumed_at is None
            and otp.expires_at > now
        ]
        return active[-1] if active else None

    async def increment_attempts(self, otp: SimpleNamespace) -> None:
        otp.attempts += 1

    async def consume(self, otp: SimpleNamespace, now: datetime) -> None:
        otp.consumed_at = now


class FakeOtpDelivery:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send_password_reset_otp(
        self,
        *,
        destination: str,
        otp_code: str,
        expires_at: datetime,
    ) -> None:
        self.sent.append(
            {
                "destination": destination,
                "otp_code": otp_code,
                "expires_at": expires_at,
            }
        )


def make_service() -> tuple[
    AuthService,
    SimpleNamespace,
    FakePasswordResetOtpRepository,
    FakeOtpDelivery,
]:
    user = SimpleNamespace(
        id="user-1",
        email="doctor@example.com",
        hashed_password="old-hash",
        is_active=True,
    )
    otp_repo = FakePasswordResetOtpRepository()
    delivery = FakeOtpDelivery()
    service = AuthService(
        users=FakeUserRepository(user),
        password_reset_otps=otp_repo,
        otp_delivery=delivery,
        settings=Settings(SECRET_KEY="test-secret"),
    )
    return service, user, otp_repo, delivery


@pytest.mark.asyncio
async def test_forgot_password_generates_and_sends_email_otp() -> None:
    service, _user, otp_repo, delivery = make_service()

    response = await service.request_password_reset(
        ForgotPasswordRequest(email="doctor@example.com")
    )

    assert response.message == "If an account exists, a password reset OTP has been sent."
    assert len(otp_repo.otps) == 1
    assert len(delivery.sent) == 1
    assert delivery.sent[0]["destination"] == "doctor@example.com"
    assert len(delivery.sent[0]["otp_code"]) == 6
    assert otp_repo.otps[0].otp_hash != delivery.sent[0]["otp_code"]


@pytest.mark.asyncio
async def test_reset_password_with_valid_otp_updates_password() -> None:
    service, user, otp_repo, delivery = make_service()
    await service.request_password_reset(ForgotPasswordRequest(email="doctor@example.com"))
    otp_code = delivery.sent[0]["otp_code"]

    response = await service.reset_password(
        ResetPasswordRequest(
            email="doctor@example.com",
            otp_code=otp_code,
            new_password="new-strong-password",
        )
    )

    assert response.message == "Password has been reset successfully."
    assert verify_password("new-strong-password", user.hashed_password)
    assert otp_repo.otps[0].consumed_at is not None


@pytest.mark.asyncio
async def test_reset_password_with_invalid_otp_is_rejected() -> None:
    service, user, otp_repo, _delivery = make_service()
    await service.request_password_reset(ForgotPasswordRequest(email="doctor@example.com"))

    with pytest.raises(HTTPException) as exc_info:
        await service.reset_password(
            ResetPasswordRequest(
                email="doctor@example.com",
                otp_code="000000",
                new_password="new-strong-password",
            )
        )

    assert exc_info.value.status_code == 400
    assert user.hashed_password == "old-hash"
    assert otp_repo.otps[0].attempts == 1
