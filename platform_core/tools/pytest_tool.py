"""PytestTool – a stub tool that would run pytest inside a sandbox.

The implementation is deterministic and replay‑safe: it validates the request
using ``PytestToolContract``, runs a stubbed ``SandboxRuntime`` command and
returns a typed ``PytestToolResult``. An artifact is created via the provided
``ArtifactRepository`` and a ``tool_completed`` log entry is emitted for
observability.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict

import structlog

from ..contracts.base_tool_contract import BaseToolContract
from ..contracts.tool_models import ToolRequest, ToolResult
from ..contracts.tool_registry import ToolRegistry
from ..sandbox.runtime import SandboxRuntime
from ..sandbox.models import ResourceQuota, ExecutionPolicy
from ..repositories.artifact_repo import ArtifactRepository
from ..schemas.artifact import ArtifactSchema, ArtifactMetadata
from ..contracts.tool_enums import ToolStatus

logger = structlog.get_logger(__name__)


class PytestToolContract(BaseToolContract):
    """Contract defining input and output for the Pytest tool."""

    class Input(BaseToolContract.Input):
        path: str
        timeout_seconds: int = 30

    class Output(BaseToolContract.Output):
        tests_run: int
        tests_passed: int
        tests_failed: int
        duration_ms: int
