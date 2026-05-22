from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_otp import PasswordResetOtp


class PasswordResetOtpRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def invalidate_active_for_user(self, user_id: str, now: datetime) -> None:
        await self.session.execute(
            update(PasswordResetOtp)
            .where(
                PasswordResetOtp.user_id == user_id,
                PasswordResetOtp.consumed_at.is_(None),
            )
            .values(consumed_at=now)
        )

    async def create(
        self,
        *,
        user_id: str,
        delivery_channel: str,
        destination: str,
        otp_hash: str,
        expires_at: datetime,
    ) -> PasswordResetOtp:
        otp = PasswordResetOtp(
            user_id=user_id,
            delivery_channel=delivery_channel,
            destination=destination,
            otp_hash=otp_hash,
            expires_at=expires_at,
        )
        self.session.add(otp)
        await self.session.flush()
        await self.session.refresh(otp)
        return otp

    async def get_latest_active(
        self,
        *,
        user_id: str,
        delivery_channel: str,
        now: datetime,
    ) -> PasswordResetOtp | None:
        result = await self.session.execute(
            select(PasswordResetOtp)
            .where(
                PasswordResetOtp.user_id == user_id,
                PasswordResetOtp.delivery_channel == delivery_channel,
                PasswordResetOtp.consumed_at.is_(None),
                PasswordResetOtp.expires_at > now,
            )
            .order_by(PasswordResetOtp.created_at.desc())
        )
        return result.scalars().first()

    async def increment_attempts(self, otp: PasswordResetOtp) -> None:
        otp.attempts += 1
        await self.session.flush()

    async def consume(self, otp: PasswordResetOtp, now: datetime) -> None:
        otp.consumed_at = now
        await self.session.flush()
