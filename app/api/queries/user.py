from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.user import User
from app.models.user_practice import UserPractice
from app.schemas.user import MembershipCreate, UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.practice_memberships.of_type(UserPractice)))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.practice_memberships.of_type(UserPractice)))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, payload: UserCreate) -> User:
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            first_name=payload.first_name,
            middle_name=payload.middle_name,
            last_name=payload.last_name,
            full_name=f"{payload.first_name} {payload.last_name}",
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def create_membership(
        self, user_id: str, payload: MembershipCreate
    ) -> UserPractice:
        membership = UserPractice(
            user_id=user_id,
            practice_id=payload.practice_id,
            role=payload.role,
        )
        self.session.add(membership)
        await self.session.flush()
        await self.session.refresh(membership)
        return membership

    async def update_password(self, user: User, password: str) -> User:
        user.hashed_password = hash_password(password)
        await self.session.flush()
        await self.session.refresh(user)
        return user
