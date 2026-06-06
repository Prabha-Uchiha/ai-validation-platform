"""Tool executor implementation.

The executor validates a ``ToolRequest`` against the registered tool contract,
creates a job via ``ToolExecutionLifecycle`` and returns a stub ``ToolResult``.
All operations are deterministic and side‑effect free except for persisting the
artifact via the repository.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from ..contracts.tool_models import ToolRequest, ToolResult
from ..contracts.tool_registry import ToolRegistry
from ..execution.context import ExecutionContext
from ..execution.lifecycle import ToolExecutionLifecycle
from ..contracts.base_tool_contract import BaseToolContract


class ToolExecutor:
    """Execute a tool within an execution context.

    The executor does **not** run real sandboxed code; it returns a stub result
    that satisfies the contract. This keeps the sprint focused on the runtime
    foundation while remaining replay‑safe.
    """

    def __init__(self, registry: ToolRegistry, lifecycle: ToolExecutionLifecycle) -> None:
        self.registry = registry
        self.lifecycle = lifecycle

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def validate_request(self, request: ToolRequest) -> None:
        """Validate the request payload against the tool's contract.

        Raises ``ValueError`` if validation fails.
        """
        definition = self.registry.get_definition(request.tool_id)
        # Resolve the contract class from the stored import path.
        contract_cls = BaseToolContract.resolve_contract(definition.contract)
        # Use the contract's ``validate_input`` method.
        contract_cls.validate_input(request.payload)

    def execute(self, context: ExecutionContext, request: ToolRequest) -> ToolResult:
        """Execute the tool and return a stub ``ToolResult``.

        The method creates a job, validates the request, stores a dummy artifact
        and returns a ``ToolResult`` with status ``SUCCESS``.
        """
        # Validate first
        self.validate_request(request)

        # Create job record
        job = self.lifecycle.create_job(context, request.tool_id, request.payload)

        # Stub result – in a real system this would be the output of the tool.
        result = ToolResult(
            execution_id=request.execution_id,
            tool_id=request.tool_id,
            status=ToolStatus.SUCCESS,
            output={"stub": True},
            correlation_id=request.correlation_id,
            completed_at=datetime.utcnow(),
        )

        # Store artifact (dummy URI)
        artifact_uri = f"stub://{uuid.uuid4()}"
        self.lifecycle.complete_job(job.job_id, result, artifact_uri)
        return result

    def store_artifact(self, result: ToolResult, uri: str) -> None:
        """Convenience method to store an artifact for a given result.
        """
        # Not used directly in this sprint – kept for API completeness.
        raise NotImplementedError()
