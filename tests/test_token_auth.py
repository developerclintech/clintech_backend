from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest

from app.api.blc.auth import AuthService
from app.core.config import Settings
from app.core.security import create_access_token, decode_access_token, hash_password
from app.schemas.auth import LoginRequest

SETTINGS = Settings(SECRET_KEY="test-secret-key-for-token-tests!")


# ---------------------------------------------------------------------------
# Security layer — create / decode roundtrip
# ---------------------------------------------------------------------------


def test_token_carries_token_version() -> None:
    token = create_access_token("user-abc", token_version=3, settings=SETTINGS)
    user_id, tv = decode_access_token(token, SETTINGS)
    assert user_id == "user-abc"
    assert tv == 3


def test_token_version_zero_roundtrips() -> None:
    token = create_access_token("user-xyz", token_version=0, settings=SETTINGS)
    user_id, tv = decode_access_token(token, SETTINGS)
    assert user_id == "user-xyz"
    assert tv == 0


def test_decode_legacy_token_without_tv_defaults_to_zero() -> None:
    """Tokens issued before token_version was added must decode cleanly as tv=0."""
    payload = {
        "sub": "user-legacy",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }
    old_token = jwt.encode(payload, SETTINGS.SECRET_KEY, algorithm=SETTINGS.JWT_ALGORITHM)
    user_id, tv = decode_access_token(old_token, SETTINGS)
    assert user_id == "user-legacy"
    assert tv == 0


def test_different_token_versions_produce_different_tokens() -> None:
    t1 = create_access_token("user-1", token_version=0, settings=SETTINGS)
    t2 = create_access_token("user-1", token_version=1, settings=SETTINGS)
    assert t1 != t2


# ---------------------------------------------------------------------------
# Fakes for AuthService login tests
# ---------------------------------------------------------------------------


class FakeLoginUserRepo:
    def __init__(self, user: SimpleNamespace) -> None:
        self._user = user
        self.relogin_writes: list[bool] = []

    async def get_by_email(self, email: str) -> SimpleNamespace | None:
        return self._user if self._user.email == email else None

    async def set_required_relogin(self, user: SimpleNamespace, value: bool) -> SimpleNamespace:
        user.required_relogin = value
        self.relogin_writes.append(value)
        return user


class FakeOtpDelivery:
    async def send_password_reset_otp(self, *, destination, otp_code, expires_at) -> None:
        pass


def make_user(*, token_version: int = 0, required_relogin: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        id="user-1",
        email="user@example.com",
        hashed_password=hash_password("correct-password"),
        is_active=True,
        token_version=token_version,
        required_relogin=required_relogin,
    )


def make_auth_service(user: SimpleNamespace) -> tuple[AuthService, FakeLoginUserRepo]:
    repo = FakeLoginUserRepo(user)
    service = AuthService(
        users=repo,
        password_reset_otps=None,  # type: ignore[arg-type]
        otp_delivery=FakeOtpDelivery(),
        settings=SETTINGS,
    )
    return service, repo


# ---------------------------------------------------------------------------
# Login — token_version embedding
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_token_embeds_current_token_version() -> None:
    user = make_user(token_version=4)
    service, _ = make_auth_service(user)

    resp = await service.login(LoginRequest(email="user@example.com", password="correct-password"))
    _, tv = decode_access_token(resp.access_token, SETTINGS)

    assert tv == 4


@pytest.mark.asyncio
async def test_login_after_password_reset_token_version_is_incremented() -> None:
    """After a password reset the stored token_version is 1.
    A fresh login must embed that new version, so old tokens are rejected."""
    user = make_user(token_version=1)
    service, _ = make_auth_service(user)

    resp = await service.login(LoginRequest(email="user@example.com", password="correct-password"))
    _, tv = decode_access_token(resp.access_token, SETTINGS)

    assert tv == 1


# ---------------------------------------------------------------------------
# Login — required_relogin flag
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_clears_required_relogin_when_set() -> None:
    user = make_user(required_relogin=True)
    service, repo = make_auth_service(user)

    await service.login(LoginRequest(email="user@example.com", password="correct-password"))

    assert user.required_relogin is False
    assert repo.relogin_writes == [False]


@pytest.mark.asyncio
async def test_login_skips_db_write_when_relogin_already_false() -> None:
    user = make_user(required_relogin=False)
    service, repo = make_auth_service(user)

    await service.login(LoginRequest(email="user@example.com", password="correct-password"))

    assert repo.relogin_writes == []


# ---------------------------------------------------------------------------
# Token version rejection (simulating get_current_user logic)
# ---------------------------------------------------------------------------


def test_stale_token_version_is_detected() -> None:
    """Simulate what get_current_user does: compare JWT tv against DB value."""
    token = create_access_token("user-1", token_version=0, settings=SETTINGS)
    _, jwt_tv = decode_access_token(token, SETTINGS)

    db_token_version = 1  # incremented after password reset

    assert jwt_tv != db_token_version, "old token must be rejected"


def test_matching_token_version_is_accepted() -> None:
    token = create_access_token("user-1", token_version=2, settings=SETTINGS)
    _, jwt_tv = decode_access_token(token, SETTINGS)

    db_token_version = 2

    assert jwt_tv == db_token_version
