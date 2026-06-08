from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Clinics API"
    ENVIRONMENT: str = "local"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+asyncpg://clinics:clinics_dev_password@localhost:5432/clinics"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_RECYCLE_SECONDS: int = 1800

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = Field(default="json", pattern="^(json|console)$")
    ENABLE_METRICS: bool = True

    AUDIT_LOG_ENABLED: bool = True

    # JWT / Auth
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    PASSWORD_RESET_OTP_LENGTH: int = 6
    PASSWORD_RESET_OTP_EXPIRE_MINUTES: int = 10
    PASSWORD_RESET_OTP_MAX_ATTEMPTS: int = 5

    # Email delivery for password reset OTP. Later SMS delivery can implement
    # the same OtpDeliveryService protocol used by AuthService.
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "no-reply@clinics.local"
    SMTP_USE_TLS: bool = True
    SMTP_TIMEOUT_SECONDS: int = 10

    # S3
    AWS_REGION: str = "eu-west-2"
    S3_ATTACHMENT_BUCKET: str = "clintech-attachments"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
