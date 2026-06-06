import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from platform_core.schemas.execution import ExecutionState
from storage.postgres.database import Base


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    repository_url: Mapped[str]

    state: Mapped[ExecutionState] = mapped_column(
        Enum(ExecutionState)
    )


class WorkflowCheckpoint(Base):
    __tablename__ = "workflow_checkpoints"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    state: Mapped[ExecutionState] = mapped_column(Enum(ExecutionState))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON)
