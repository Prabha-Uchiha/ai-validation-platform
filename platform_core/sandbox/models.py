"""Sandbox related data models.

These models are deliberately simple and immutable to guarantee deterministic
behaviour and replay safety. They do **not** perform any real isolation – the
runtime stub will simply return a ``SandboxResult``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class ResourceQuota(BaseModel):
    """Limits for a sandboxed execution.

    Attributes
    ----------
    cpu_limit: float
        Maximum CPU cores allowed.
    memory_limit_mb: int
        Maximum memory in megabytes.
    timeout_seconds: int
        Maximum wall‑clock time before the sandbox is considered timed out.
    """

    cpu_limit: float = Field(..., description="CPU core limit")
    memory_limit_mb: int = Field(..., description="Memory limit in MB")
    timeout_seconds: int = Field(..., description="Execution timeout in seconds")

    class Config:
        frozen = True


class ExecutionPolicy(BaseModel):
    """Policy controlling what a sandbox may do.

    All fields default to ``False`` for a maximally restrictive sandbox.
    """

    allow_network: bool = Field(False, description="Permit network access")
    allow_filesystem: bool = Field(False, description="Permit filesystem access")
    allow_subprocess: bool = Field(False, description="Permit subprocess spawning")
    allow_docker: bool = Field(False, description="Permit Docker usage (stubbed)")

    class Config:
        frozen = True


class SandboxResult(BaseModel):
    """Result of a sandbox execution.

    The stub implementation always reports success with a dummy output.
    """

    success: bool = Field(..., description="Whether execution succeeded")
    exit_code: int = Field(..., description="Process exit code")
    stdout: str = Field(..., description="Standard output captured")
    stderr: str = Field(..., description="Standard error captured")

    class Config:
        frozen = True
