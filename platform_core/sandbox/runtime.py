"""Sandbox runtime foundation.

The runtime validates a supplied ``ExecutionPolicy`` and ``ResourceQuota`` and
returns a deterministic ``SandboxResult`` stub. No real isolation or command
execution is performed – this satisfies the sprint constraints while keeping
the implementation replay‑safe and observable.
"""

from __future__ import annotations

import structlog
from typing import Any

from .models import ResourceQuota, ExecutionPolicy, SandboxResult

logger = structlog.get_logger(__name__)


class SandboxRuntime:
    """Validate policies/quotas and produce a stub sandbox result.

    All methods are pure and deterministic; they log their actions for
    observability.
    """

    def __init__(self, policy: ExecutionPolicy, quota: ResourceQuota) -> None:
        self.policy = policy
        self.quota = quota

    # ---------------------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------------------
    def validate_policy(self) -> None:
        """Validate that the policy is acceptable.

        For the stub implementation we simply ensure the object is an instance
        of ``ExecutionPolicy``. Real checks would enforce security constraints.
        """
        if not isinstance(self.policy, ExecutionPolicy):
            raise TypeError("policy must be an ExecutionPolicy instance")
        logger.info("sandbox_policy_validated", policy=self.policy.dict())

    def validate_quota(self) -> None:
        """Validate that the quota values are sensible.

        Raises ``ValueError`` if any limit is non‑positive.
        """
        if self.quota.cpu_limit <= 0:
            raise ValueError("cpu_limit must be positive")
        if self.quota.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")
        if self.quota.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        logger.info("sandbox_quota_validated", quota=self.quota.dict())

    # ---------------------------------------------------------------------
    # Execution stub
    # ---------------------------------------------------------------------
    def execute(self, command: str, *args: Any, **kwargs: Any) -> SandboxResult:
        """Execute a command inside the sandbox (stub).

        The method validates policy and quota, logs the requested command and
        returns a deterministic ``SandboxResult`` indicating success.
        """
        self.validate_policy()
        self.validate_quota()
        logger.info("sandbox_execute", command=command, args=args, kwargs=kwargs)
        # Stub result – in a real implementation this would run the command.
        return SandboxResult(
            success=True,
            exit_code=0,
            stdout="stub output",
            stderr="",
        )
