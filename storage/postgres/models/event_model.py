import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from storage.postgres.database import Base

class EventRecord(Base):
    __tablename__ = "event_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    event_type: Mapped[str]
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    correlation_id: Mapped[str] = mapped_column(index=True)
