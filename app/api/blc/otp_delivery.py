from __future__ import annotations

import asyncio
import smtplib
from datetime import datetime
from email.message import EmailMessage
from typing import Protocol

import structlog
from mailjet_rest import Client as MailjetClient

from app.core.config import Settings


class OtpDeliveryService(Protocol):
    async def send_password_reset_otp(
        self,
        *,
        destination: str,
        otp_code: str,
        expires_at: datetime,
    ) -> None:
        pass


class EmailOtpDeliveryService:
    delivery_channel = "email"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = structlog.get_logger(__name__)

    async def send_password_reset_otp(
        self,
        *,
        destination: str,
        otp_code: str,
        expires_at: datetime,
    ) -> None:
        if not self.settings.SMTP_HOST:
            self.logger.warning(
                "password_reset_otp_email_delivery_skipped",
                reason="smtp_not_configured",
            )
            return

        try:
            await asyncio.to_thread(
                self._send_email,
                destination=destination,
                otp_code=otp_code,
                expires_at=expires_at,
            )
        except Exception as exc:
            self.logger.error(
                "otp_email_delivery_failed",
                destination=destination,
                error=str(exc),
            )
            raise RuntimeError("Failed to deliver OTP email.") from exc

    def _send_email(
        self,
        *,
        destination: str,
        otp_code: str,
        expires_at: datetime,
    ) -> None:
        message = EmailMessage()
        message["From"] = self.settings.SMTP_FROM_EMAIL
        message["To"] = destination
        message["Subject"] = f"{self.settings.APP_NAME} password reset OTP"
        message.set_content(
            "\n".join(
                [
                    "Use this OTP to reset your password.",
                    "",
                    f"OTP: {otp_code}",
                    f"Expires at: {expires_at.isoformat()}",
                    "",
                    "If you did not request this, you can ignore this email.",
                ]
            )
        )

        with smtplib.SMTP(
            self.settings.SMTP_HOST,
            self.settings.SMTP_PORT,
            timeout=self.settings.SMTP_TIMEOUT_SECONDS,
        ) as smtp:
            if self.settings.SMTP_USE_TLS:
                smtp.starttls()
            if self.settings.SMTP_USERNAME:
                smtp.login(
                    self.settings.SMTP_USERNAME,
                    self.settings.SMTP_PASSWORD or "",
                )
            smtp.send_message(message)


class MailjetOtpDeliveryService:
    delivery_channel = "email"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = structlog.get_logger(__name__)

    async def send_password_reset_otp(
        self,
        *,
        destination: str,
        otp_code: str,
        expires_at: datetime,
    ) -> None:
        body = "\n".join(
            [
                "Use this OTP to reset your password.",
                "",
                f"OTP: {otp_code}",
                f"Expires at: {expires_at.isoformat()}",
                "",
                "If you did not request this, you can ignore this email.",
            ]
        )
        data = {
            "Messages": [
                {
                    "From": {
                        "Email": self.settings.MJ_FROM_EMAIL,
                        "Name": self.settings.MJ_FROM_NAME,
                    },
                    "To": [{"Email": destination}],
                    "Subject": f"{self.settings.APP_NAME} password reset OTP",
                    "TextPart": body,
                }
            ]
        }
        try:
            result = await asyncio.to_thread(self._send_via_mailjet, data)
        except Exception as exc:
            self.logger.error(
                "otp_email_delivery_failed",
                destination=destination,
                error=str(exc),
            )
            raise RuntimeError("Failed to deliver OTP email.") from exc

        if result.status_code != 200:
            self.logger.error(
                "mailjet_api_error",
                destination=destination,
                status=result.status_code,
                body=result.json(),
            )
            raise RuntimeError("Failed to deliver OTP email.")

        self.logger.info(
            "otp_email_delivered_via_mailjet",
            destination=destination,
            status=result.status_code,
        )

    def _send_via_mailjet(self, data: dict):
        client = MailjetClient(
            auth=(self.settings.MJ_APIKEY_PUBLIC, self.settings.MJ_APIKEY_PRIVATE),
            version="v3.1",
        )
        return client.send.create(data=data)
