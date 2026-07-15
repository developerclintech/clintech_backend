from __future__ import annotations

from fastapi import HTTPException, status

from app.api.queries.practice import PracticeRepository
from app.models.user import User
from app.schemas.practice import PracticeCreate, PracticeRead, PracticeStatusUpdate, PracticeUpdate
from utils.auth_functions import is_super_admin


class PracticeService:
    def __init__(self, *, practices: PracticeRepository) -> None:
        self.practices = practices

    async def create_practice(
        self, payload: PracticeCreate, current_user: User
    ) -> PracticeRead:
        practice = await self.practices.create(payload)
        return PracticeRead.model_validate(practice)

    async def get_practice(
        self, practice_id: str, current_user: User
    ) -> PracticeRead:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )
        return PracticeRead.model_validate(practice)

    async def list_practices(
        self, current_user: User, exclude_user_id: str | None = None
    ) -> list[PracticeRead]:
        practice_ids: list[str] | None = None
        if not is_super_admin(current_user):
            practice_ids = [
                membership.practice_id
                for membership in current_user.practice_memberships
                if membership.is_active and membership.practice_id is not None
            ]
        practices = await self.practices.get_all(
            practice_ids=practice_ids, exclude_user_id=exclude_user_id
        )
        return [PracticeRead.model_validate(p) for p in practices]

    async def update_practice(
        self, practice_id: str, payload: PracticeUpdate, current_user: User
    ) -> PracticeRead:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )
        practice = await self.practices.update(practice, payload)
        return PracticeRead.model_validate(practice)

    async def update_practice_status(
        self, practice_id: str, payload: PracticeStatusUpdate, current_user: User
    ) -> PracticeRead:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )
        practice = await self.practices.set_status(practice, payload.is_active)
        return PracticeRead.model_validate(practice)

    async def delete_practice(self, practice_id: str, current_user: User) -> None:
        practice = await self.practices.get_by_id(practice_id)
        if practice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found.",
            )
        await self.practices.delete(practice)
