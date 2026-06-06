"""Execution job model.

Represents a single tool execution within an execution context. The model is
immutable once persisted, but the lifecycle class updates the underlying record
in the database.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..contracts.tool_enums import ToolStatus


class ExecutionJob(BaseModel):
    """Job record for a tool execution.

    Attributes
    ----------
    job_id: uuid.UUID
        Primary key for the job.
    tool_id: str
        Identifier of the tool to be executed.
    request: Dict[str, Any]
        The raw request payload (validated elsewhere).
    status: ToolStatus
        Current status of the job.
    created_at: datetime
        Timestamp when the job was created.
    updated_at: datetime
        Timestamp of the last status update.
    """

    job_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Job identifier")
    tool_id: str = Field(..., description="Tool identifier")
    request: Dict[str, Any] = Field(..., description="Validated tool request payload")
    status: ToolStatus = Field(default=ToolStatus.SKIPPED, description="Job status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")

    class Config:
        frozen = True
