from uuid import UUID
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from storage.postgres.models.event_model import EventRecord

class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        event_id: UUID,
        execution_id: UUID,
        event_type: str,
        payload: dict[str, Any],
        correlation_id: str,
    ) -> EventRecord:
        """
        Persists an event record to the database.
        """
        event = EventRecord(
            id=event_id,
            execution_id=execution_id,
            event_type=event_type,
            payload_json=payload,
            correlation_id=correlation_id,
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_by_execution(self, execution_id: UUID) -> Sequence[EventRecord]:
        """
        Retrieves all events for a given execution, ordered by timestamp.
        """
        result = await self.session.execute(
            select(EventRecord)
            .where(EventRecord.execution_id == execution_id)
            .order_by(EventRecord.timestamp)
        )
        return result.scalars().all()
