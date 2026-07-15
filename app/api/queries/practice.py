from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.practice import Practice
from app.models.user_practice import UserPractice
from app.schemas.practice import PracticeCreate, PracticeUpdate


class PracticeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: PracticeCreate) -> Practice:
        practice = Practice(
            name=payload.name,
            ods_code=payload.ods_code,
            notice=payload.notice,
            phone=payload.phone,
            website=payload.website,
            email=payload.email,
            address=payload.address,
            practice_hours=payload.practice_hours,
            is_emis_enabled=payload.is_emis_enabled,
        )
        self.session.add(practice)
        await self.session.flush()
        await self.session.refresh(practice)
        return practice

    async def get_by_id(self, practice_id: str) -> Practice | None:
        result = await self.session.execute(
            select(Practice).where(Practice.id == practice_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        practice_ids: list[str] | None = None,
        exclude_user_id: str | None = None,
    ) -> list[Practice]:
        stmt = select(Practice).order_by(Practice.created_at.desc())
        if practice_ids is not None:
            stmt = stmt.where(Practice.id.in_(practice_ids))
        if exclude_user_id is not None:
            assigned_practice_ids = select(UserPractice.practice_id).where(
                UserPractice.user_id == exclude_user_id,
                UserPractice.practice_id.is_not(None),
            )
            stmt = stmt.where(Practice.id.not_in(assigned_practice_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, practice: Practice, payload: PracticeUpdate) -> Practice:
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(practice, field, value)
        await self.session.flush()
        await self.session.refresh(practice)
        return practice

    async def set_status(self, practice: Practice, is_active: bool) -> Practice:
        practice.is_active = is_active
        await self.session.flush()
        await self.session.refresh(practice)
        return practice

    async def delete(self, practice: Practice) -> None:
        await self.session.delete(practice)
        await self.session.flush()
