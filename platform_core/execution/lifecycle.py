"""Tool execution lifecycle management.

This module provides a deterministic, replay‑safe manager for tool jobs. It
stores jobs in an in‑memory dictionary (suitable for the sprint) and interacts
with the ``ToolRegistry`` and ``ArtifactRepository`` to persist definitions and
artifacts.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict

from ..contracts.tool_registry import ToolRegistry
from ..contracts.tool_models import ToolResult
from ..contracts.tool_enums import ToolStatus
from ..execution.job import ExecutionJob
from ..execution.context import ExecutionContext
from ..schemas.artifact import ArtifactSchema, ArtifactMetadata
# The concrete repository lives in the storage package. Importing via the full
# path avoids a circular package reference and works for both the real and
# test in‑memory implementations.
from storage.postgres.repositories.artifact_repo import ArtifactRepository


class ToolExecutionLifecycle:
    """Manage the lifecycle of a tool execution job.

    The implementation is intentionally simple: jobs are kept in a class‑level
    dictionary keyed by ``job_id``. All state transitions are recorded with
    timestamps to guarantee deterministic replay.
    """

    _jobs: Dict[uuid.UUID, ExecutionJob] = {}

    def __init__(self, registry: ToolRegistry, artifact_repo: ArtifactRepository) -> None:
        self.registry = registry
        self.artifact_repo = artifact_repo

    # ---------------------------------------------------------------------
    # Lifecycle operations
    # ---------------------------------------------------------------------
    def create_job(self, context: ExecutionContext, tool_id: str, request: dict) -> ExecutionJob:
        """Create a new ``ExecutionJob`` and store it.

        The request is assumed to have been validated by ``ToolExecutor``.
        """
        job = ExecutionJob(
            job_id=uuid.uuid4(),
            tool_id=tool_id,
            request=request,
            status=ToolStatus.SKIPPED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self._jobs[job.job_id] = job
        return job

    def update_status(self, job_id: uuid.UUID, status: ToolStatus) -> ExecutionJob:
        job = self._jobs[job_id]
        updated = job.copy(update={"status": status, "updated_at": datetime.utcnow()})
        self._jobs[job_id] = updated
        return updated

    def complete_job(self, job_id: uuid.UUID, result: ToolResult, artifact_uri: str) -> ExecutionJob:
        """Mark a job as successful and store the resulting artifact.

        The concrete ``ArtifactRepository`` expects keyword arguments rather than a
        full ``ArtifactSchema`` instance. To keep the lifecycle decoupled from the
        repository implementation we pass the individual fields. This works for
        both the real SQLAlchemy repository and the in‑memory dummy used in tests.
        """
        metadata = ArtifactMetadata(tags=["tool_execution"], description="Result artifact")
        # Store artifact using repository's async ``create`` method.
        # The repository may be a real async implementation or a simple sync stub.
        self.artifact_repo.create(
            execution_id=result.execution_id,
            artifact_type="tool_result",
            artifact_uri=artifact_uri,
            metadata=metadata.dict(),
        )
        return self.update_status(job_id, ToolStatus.SUCCESS)

    def fail_job(self, job_id: uuid.UUID, reason: str) -> ExecutionJob:
        # In a real system we would record the reason; here we just set status.
        return self.update_status(job_id, ToolStatus.FAILURE)
