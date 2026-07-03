from __future__ import annotations

from fastapi import HTTPException, status

from app.api.queries.practice import PracticeRepository
from app.api.queries.user import UserRepository
from app.models.user import User
from app.schemas.user import MembershipCreate, MembershipRead, UserCreate, UserRead
from utils.auth_functions import has_role, is_super_admin
from utils.enums import UserRole


class UserService:
    def __init__(
        self, *, users: UserRepository, practices: PracticeRepository
    ) -> None:
        self.users = users
        self.practices = practices

    async def create_user(self, payload: UserCreate, current_user: User) -> UserRead:
        if await self.users.get_by_email(payload.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered.",
            )

        for assignment in payload.roles:
            practice = await self.practices.get_by_id(assignment.practice_id)
            if practice is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Practice '{assignment.practice_id}' not found.",
                )

            if not is_super_admin(current_user) and not has_role(
                current_user,
                [UserRole.PRACTICE_ADMIN],
                practice_id=assignment.practice_id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this practice.",
                )

        user = await self.users.create(payload)
        for assignment in payload.roles:
            await self.users.create_membership(
                user.id,
                MembershipCreate(
                    practice_id=assignment.practice_id, role=assignment.role
                ),
            )

        # Reload with memberships
        user = await self.users.get_by_id(user.id)
        return UserRead.model_validate(user)

    async def get_user(self, user_id: str, current_user: User) -> UserRead:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return UserRead.model_validate(user)

    async def list_users(self, current_user: User) -> list[UserRead]:
        users = await self.users.get_all()
        return [UserRead.model_validate(user) for user in users]

    async def add_membership(
        self,
        user_id: str,
        payload: MembershipCreate,
        current_user: User,
    ) -> MembershipRead:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if payload.practice_id is not None:
            practice = await self.practices.get_by_id(payload.practice_id)
            if practice is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Practice not found.",
                )
            if not is_super_admin(current_user) and not has_role(
                current_user,
                [UserRole.PRACTICE_ADMIN],
                practice_id=payload.practice_id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this practice.",
                )

        membership = await self.users.create_membership(user_id, payload)
        return MembershipRead.model_validate(membership)
