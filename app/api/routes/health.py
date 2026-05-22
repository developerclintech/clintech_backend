from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_session import get_db
from app.schemas.health import HealthCheck

router = APIRouter()


@router.get("/live", response_model=HealthCheck)
async def live() -> HealthCheck:
    return HealthCheck(status="ok")


@router.get("/ready", response_model=HealthCheck)
async def ready(session: AsyncSession = Depends(get_db)) -> HealthCheck:
    await session.execute(text("SELECT 1"))
    return HealthCheck(status="ok")
