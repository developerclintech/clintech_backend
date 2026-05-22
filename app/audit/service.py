from __future__ import annotations

from fastapi import BackgroundTasks

from app.api.queries.audit import AuditLogRepository
from app.core.db_session import AsyncSessionLocal


class AuditService:
    """Writes audit records via BackgroundTasks so the HTTP response is not blocked."""

    def __init__(self, background_tasks: BackgroundTasks) -> None:
        self.background_tasks = background_tasks

    def record(
        self,
        *,
        actor_id: str | None,
        action: str,
        entity_type: str,
        entity_id: str | None,
        trace_id: str | None,
        metadata: dict | None = None,
    ) -> None:
        self.background_tasks.add_task(
            self._write,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            trace_id=trace_id,
            metadata=metadata,
        )

    @staticmethod
    async def _write(
        *,
        actor_id: str | None,
        action: str,
        entity_type: str,
        entity_id: str | None,
        trace_id: str | None,
        metadata: dict | None,
    ) -> None:
        async with AsyncSessionLocal() as session:
            try:
                await AuditLogRepository(session).record(
                    actor_id=actor_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    trace_id=trace_id,
                    metadata=metadata,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                raise
