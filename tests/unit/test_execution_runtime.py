import uuid
import pytest
from datetime import datetime

from platform_core.execution.context import ExecutionContext
from platform_core.execution.executor import ToolExecutor
from platform_core.execution.lifecycle import ToolExecutionLifecycle
from platform_core.contracts.tool_models import ToolRequest
from platform_core.contracts.tool_registry import ToolRegistry
from platform_core.contracts.base_tool_contract import BaseToolContract
from pydantic import BaseModel
from platform_core.contracts.tool_enums import ToolStatus
from platform_core.schemas.artifact import ArtifactMetadata, ArtifactSchema


class DummyContract(BaseToolContract):
    class Input(BaseModel):
        value: int

    class Output(BaseModel):
        result: int


class DummyArtifactRepo:
    """Very small in‑memory artifact repository for testing purposes.

    The real ``ArtifactRepository`` is async, but the execution lifecycle uses
    a synchronous call for simplicity in this sprint. Therefore the dummy repo
    provides a regular ``create`` method.
    """

    def __init__(self) -> None:
        self.created: list[ArtifactSchema] = []

    def create(self, *, execution_id: uuid.UUID, artifact_type: str, artifact_uri: str, metadata: dict | None = None) -> ArtifactSchema:  # type: ignore[override]
        artifact = ArtifactSchema(
            artifact_id=uuid.uuid4(),
            execution_id=execution_id,
            artifact_type=artifact_type,
            artifact_uri=artifact_uri,
            artifact_metadata=ArtifactMetadata(tags=["test"], description="test artifact"),
            created_at=datetime.utcnow(),
        )
        self.created.append(artifact)
        return artifact


@pytest.fixture
def registry() -> ToolRegistry:
    reg = ToolRegistry()
    # Register a dummy tool with the DummyContract
    reg.register(
        tool_id="dummy",
        name="Dummy Tool",
        capability="test",
        version="1.0",
        contract=DummyContract,
    )
    return reg


@pytest.mark.asyncio
async def test_tool_executor_flow(registry: ToolRegistry) -> None:
    # Setup execution context and request
    exec_id = uuid.uuid4()
    ctx = ExecutionContext(
        execution_id=exec_id,
        correlation_id=uuid.uuid4(),
        workflow_state="started",
        metadata=None,
    )
    request = ToolRequest(
        execution_id=exec_id,
        tool_id="dummy",
        payload={"value": 1},
        correlation_id=str(uuid.uuid4()),
    )

    artifact_repo = DummyArtifactRepo()
    lifecycle = ToolExecutionLifecycle(registry, artifact_repo)  # type: ignore[arg-type]
    executor = ToolExecutor(registry, lifecycle)

    result = executor.execute(ctx, request)

    assert result.status == ToolStatus.SUCCESS
    # Ensure an artifact was stored
    assert len(artifact_repo.created) == 1