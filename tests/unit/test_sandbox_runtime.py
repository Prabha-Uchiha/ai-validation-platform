import pytest

from platform_core.sandbox.models import ResourceQuota, ExecutionPolicy, SandboxResult
from platform_core.sandbox.runtime import SandboxRuntime


def test_sandbox_successful_execution() -> None:
    quota = ResourceQuota(cpu_limit=1.0, memory_limit_mb=256, timeout_seconds=30)
    policy = ExecutionPolicy(allow_network=False, allow_filesystem=False, allow_subprocess=False, allow_docker=False)
    runtime = SandboxRuntime(policy=policy, quota=quota)
    result = runtime.execute("echo", "hello")
    assert isinstance(result, SandboxResult)
    assert result.success is True
    assert result.exit_code == 0
    assert result.stdout == "stub output"


def test_invalid_quota_raises() -> None:
    quota = ResourceQuota(cpu_limit=0, memory_limit_mb=256, timeout_seconds=30)
    policy = ExecutionPolicy()
    runtime = SandboxRuntime(policy=policy, quota=quota)
    with pytest.raises(ValueError):
        runtime.validate_quota()
