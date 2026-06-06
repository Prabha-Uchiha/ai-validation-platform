"""Repository for immutable ArtifactModel.

Provides a thin abstraction over SQLAlchemy sessions.  All methods are
type‑annotated and return immutable Pydantic representations (defined later).
"""

from __future__ import annotations

import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.artifact_model import ArtifactModel
from platform_core.schemas.artifact import ArtifactSchema


class ArtifactRepository:
    """Repository pattern for ArtifactModel.

    The repository is deliberately simple – it only supports creation and
    read‑only queries to preserve replay‑safety.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        execution_id: uuid.UUID,
        artifact_type: str,
        artifact_uri: str,
        metadata: Dict[str, Any] | None = None,
    ) -> ArtifactSchema:
        """Create a new artifact record and return its immutable schema."""
        model = ArtifactModel(
            execution_id=execution_id,
            artifact_type=artifact_type,
            artifact_uri=artifact_uri,
            metadata=metadata,
        )
        self._session.add(model)
        await self._session.flush()
        return ArtifactSchema.from_orm(model)

    async def get_by_id(self, artifact_id: uuid.UUID) -> Optional[ArtifactSchema]:
        result = await self._session.get(ArtifactModel, artifact_id)
        return ArtifactSchema.from_orm(result) if result else None

    async def list_by_execution(self, execution_id: uuid.UUID) -> List[ArtifactSchema]:
        # The equality expression is valid at runtime; ignore type checking here.
        stmt = select(ArtifactModel).where(ArtifactModel.execution_id == execution_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [ArtifactSchema.from_orm(m) for m in models]
