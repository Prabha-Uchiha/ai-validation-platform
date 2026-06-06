from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from platform_core.schemas.execution import ExecutionState
from storage.postgres.models.execution_model import Execution


class ExecutionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, execution_id: UUID, repository_url: str, state: ExecutionState
    ) -> Execution:
        """
        Creates a new execution record in the database.
        """
        execution = Execution(
            id=execution_id,
            repository_url=repository_url,
            state=state,
        )
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def get_by_id(self, execution_id: UUID) -> Execution | None:
        """
        Retrieves an execution record by its ID.
        """
        result = await self.session.execute(
            select(Execution).where(Execution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def update_state(self, execution_id: UUID, state: ExecutionState) -> None:
        """
        Updates the state of an execution record.
        """
        await self.session.execute(
            update(Execution)
            .where(Execution.id == execution_id)
            .values(state=state),
        )
        await self.session.commit()
