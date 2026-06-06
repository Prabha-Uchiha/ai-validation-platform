"""Pydantic models for tool invocation and results.

These models are deliberately simple and deterministic – they contain only
primitive types and references to the ``BaseToolContract`` for validation.
No business logic is performed here; the models are pure data containers.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from typing import Any

from .tool_enums import ToolStatus


class ToolRequest(BaseModel):
    """Request to execute a tool.

    The ``payload`` field must conform to the ``Input`` model of the tool's
    contract.  Validation is performed by the caller using
    ``BaseToolContract.validate_input``.
    """

    execution_id: UUID = Field(..., description="Execution to which the tool belongs")
    tool_id: str = Field(..., description="Identifier of the tool to run")
    payload: dict[str, Any] = Field(..., description="Raw input payload for the tool")
    correlation_id: str = Field(..., description="Correlation ID for tracing")
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    contract_version: int = Field(1, description="Version of the tool request contract schema")


class ToolResult(BaseModel):
    """Result produced by a tool.

    ``output`` must match the ``Output`` model of the corresponding contract.
    ``status`` indicates whether the tool succeeded, failed, or was skipped.
    """

    execution_id: UUID = Field(..., description="Execution to which the result belongs")
    tool_id: str = Field(..., description="Identifier of the tool that was run")
    status: ToolStatus = Field(..., description="Runtime status of the tool execution")
    output: dict[str, Any] = Field(..., description="Serialized output matching the contract's Output model")
    correlation_id: str = Field(..., description="Correlation ID for tracing")
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    contract_version: int = Field(1, description="Version of the tool result contract schema")
