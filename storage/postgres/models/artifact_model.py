"""SQLAlchemy model for immutable artifacts.

The model is deliberately simple and immutable – once created the row is not
updated.  This guarantees replay‑safety because the same artifact can be read
multiple times without side effects.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from typing import Dict, Any

from ..database import Base


class ArtifactModel(Base):
    """Immutable artifact persisted for an execution.

    Attributes
    ----------
    artifact_id: UUID primary key
    execution_id: UUID foreign key to ``execution`` table
    artifact_type: str – logical type of the artifact (e.g., "tool_result")
    artifact_uri: str – location where the artifact payload is stored
    metadata: JSON – arbitrary key/value data supplied by the producer
    created_at: datetime – timestamp of creation (UTC)
    """

    __tablename__ = "artifact"

    artifact_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("execution.execution_id"), nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String, nullable=False)
    artifact_uri: Mapped[str] = mapped_column(String, nullable=False)
    # Renamed to avoid conflict with DeclarativeBase.metadata attribute
    artifact_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
