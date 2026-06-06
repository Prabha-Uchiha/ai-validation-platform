"""Execution context model.

The context carries information that is shared across the lifetime of a workflow
execution. It is deliberately simple and immutable to guarantee replay safety.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """Immutable context for a workflow execution.

    Attributes
    ----------
    execution_id: uuid.UUID
        Unique identifier for the execution.
    correlation_id: uuid.UUID
        Identifier used to correlate events across the system.
    workflow_state: str
        Arbitrary string representing the current state of the workflow.
    metadata: Optional[Dict[str, Any]]
        Additional metadata supplied by the orchestrator.
    """

    execution_id: uuid.UUID = Field(..., description="Execution identifier")
    correlation_id: uuid.UUID = Field(..., description="Correlation identifier for tracing")
    workflow_state: str = Field(..., description="Current workflow state")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Extra metadata")

    class Config:
        frozen = True  # make immutable for replay safety
