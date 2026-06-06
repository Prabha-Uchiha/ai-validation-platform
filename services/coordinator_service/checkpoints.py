from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Any

from platform_core.schemas.execution import ExecutionState
from storage.postgres.repositories.checkpoint_repo import CheckpointRepository

@dataclass(frozen=True)
class WorkflowCheckpoint:
    execution_id: UUID
    state: ExecutionState
    timestamp: datetime
    metadata: dict[str, Any]


class CheckpointManager:
    def __init__(self, repository: CheckpointRepository) -> None:
        self.repository = repository

    async def create_checkpoint(
        self,
        execution_id: UUID,
        state: ExecutionState,
        metadata: dict[str, Any],
    ) -> WorkflowCheckpoint:
        """
        Creates a new checkpoint for the workflow and persists it.
        """
        db_checkpoint = await self.repository.create(
            execution_id=execution_id,
            state=state,
            metadata=metadata,
        )

        return WorkflowCheckpoint(
            execution_id=db_checkpoint.execution_id,
            state=db_checkpoint.state,
            timestamp=db_checkpoint.timestamp,
            metadata=db_checkpoint.metadata_json,
        )

    async def get_latest_checkpoint(self, execution_id: UUID) -> WorkflowCheckpoint | None:
        """
        Retrieves the most recent checkpoint for an execution to support replay.
        """
        db_checkpoint = await self.repository.get_latest(execution_id)
        if not db_checkpoint:
            return None

        return WorkflowCheckpoint(
            execution_id=db_checkpoint.execution_id,
            state=db_checkpoint.state,
            timestamp=db_checkpoint.timestamp,
            metadata=db_checkpoint.metadata_json,
        )

    async def get_execution_history(self, execution_id: UUID) -> list[WorkflowCheckpoint]:
        """
        Retrieves all checkpoints for an execution for auditing and replay analysis.
        """
        db_checkpoints = await self.repository.get_all_for_execution(execution_id)

        return [
            WorkflowCheckpoint(
                execution_id=cp.execution_id,
                state=cp.state,
                timestamp=cp.timestamp,
                metadata=cp.metadata_json,
            )
            for cp in db_checkpoints
        ]
