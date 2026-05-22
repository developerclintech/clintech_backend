"""
Seed a super_admin user with a global membership (practice_id = NULL).

Usage:
    python -m scripts.seed_super_admin
    python -m scripts.seed_super_admin --email you@example.com --password secret123 \
        --first-name Jane --last-name Doe
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_session import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.user_practice import UserPractice
from utils.enums import UserRole


async def seed(email: str, password: str, first_name: str, last_name: str) -> None:
    async with AsyncSessionLocal() as session:
        await _create_super_admin(session, email, password, first_name, last_name)
        await session.commit()


async def _create_super_admin(
    session: AsyncSession,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> None:
    existing = await session.scalar(select(User).where(User.email == email))
    if existing:
        print(f"User already exists: {email}")
        return

    user = User(
        email=email,
        hashed_password=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        full_name=f"{first_name} {last_name}",
        is_active=True,
    )
    session.add(user)
    await session.flush()

    membership = UserPractice(
        user_id=user.id,
        practice_id=None,
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    session.add(membership)

    print(f"Super admin created: {email} (id={user.id})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed a super_admin user")
    parser.add_argument("--email",      default="admin@example.com")
    parser.add_argument("--password",   default="Admin@1234")
    parser.add_argument("--first-name", default="Super", dest="first_name")
    parser.add_argument("--last-name",  default="Admin", dest="last_name")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(seed(args.email, args.password, args.first_name, args.last_name))
