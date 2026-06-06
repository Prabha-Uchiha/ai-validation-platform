from uuid import UUID
from typing import Any, Sequence

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from platform_core.schemas.execution import ExecutionState
from storage.postgres.models.execution_model import WorkflowCheckpoint

class CheckpointRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        execution_id: UUID,
        state: ExecutionState,
        metadata: dict[str, Any]
    ) -> WorkflowCheckpoint:
        """
        Creates a new workflow checkpoint.
        """
        checkpoint = WorkflowCheckpoint(
            execution_id=execution_id,
            state=state,
            metadata_json=metadata,
        )
        self.session.add(checkpoint)
        await self.session.commit()
        await self.session.refresh(checkpoint)
        return checkpoint

    async def get_latest(self, execution_id: UUID) -> WorkflowCheckpoint | None:
        """
        Retrieves the most recent checkpoint for a given execution.
        """
        result = await self.session.execute(
            select(WorkflowCheckpoint)
            .where(WorkflowCheckpoint.execution_id == execution_id)
            .order_by(desc(WorkflowCheckpoint.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_for_execution(self, execution_id: UUID) -> Sequence[WorkflowCheckpoint]:
        """
        Retrieves all checkpoints for a given execution, ordered by timestamp.
        """
        result = await self.session.execute(
            select(WorkflowCheckpoint)
            .where(WorkflowCheckpoint.execution_id == execution_id)
            .order_by(WorkflowCheckpoint.timestamp)
        )
        return result.scalars().all()
