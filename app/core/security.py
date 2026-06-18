from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import Settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, token_version: int, settings: Settings) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload: dict[str, Any] = {"sub": user_id, "tv": token_version, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str, settings: Settings) -> tuple[str, int]:
    """Decode a JWT and return (user_id, token_version). Raises jwt.PyJWTError on invalid token."""
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    return str(payload["sub"]), int(payload.get("tv", 0))


def hash_otp(otp_code: str, settings: Settings) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        otp_code.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_otp(plain: str, hashed: str, settings: Settings) -> bool:
    return hmac.compare_digest(hash_otp(plain, settings), hashed)
