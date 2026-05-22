from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(
        self,
        *,
        actor_id: str | None,
        action: str,
        entity_type: str,
        entity_id: str | None,
        trace_id: str | None,
        metadata: dict | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            trace_id=trace_id,
            metadata_json=metadata or {},
        )
        self.session.add(audit_log)
        await self.session.flush()
        return audit_log
