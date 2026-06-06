import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock

from platform_core.schemas.execution import ExecutionState
from services.coordinator_service.coordinator import Coordinator
from event_bus.publishers.publisher import EventPublisher
from storage.postgres.repositories.execution_repo import ExecutionRepository
from storage.postgres.repositories.event_repo import EventRepository
from storage.postgres.repositories.checkpoint_repo import CheckpointRepository
from services.coordinator_service.checkpoints import CheckpointManager
from services.coordinator_service.state_machine import WorkflowStateMachine
from event_bus.redis_streams.client import RedisStreamClient

@pytest.mark.asyncio
async def test_coordinator_start_execution() -> None:
    # Mocks
    mock_execution_repo = AsyncMock(spec=ExecutionRepository)
    mock_event_repo = AsyncMock(spec=EventRepository)
    mock_checkpoint_repo = AsyncMock(spec=CheckpointRepository)
    mock_stream_client = AsyncMock(spec=RedisStreamClient)

    checkpoint_manager = CheckpointManager(mock_checkpoint_repo)
    state_machine = WorkflowStateMachine()
    event_publisher = EventPublisher(mock_event_repo, mock_stream_client)

    coordinator = Coordinator(
        execution_repo=mock_execution_repo,
        event_repo=mock_event_repo,
        checkpoint_manager=checkpoint_manager,
        state_machine=state_machine,
        event_publisher=event_publisher,
    )

    repo_url = "https://github.com/test/repo"
    branch = "main"

    execution_id = await coordinator.start_execution(repo_url, branch)

    assert isinstance(execution_id, UUID)
    mock_execution_repo.create.assert_called_once()
    mock_event_repo.create.assert_called_once()
    mock_stream_client.publish.assert_called_once()
    mock_checkpoint_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_coordinator_transition_execution() -> None:
    # Mocks
    mock_execution_repo = AsyncMock(spec=ExecutionRepository)
    mock_event_repo = AsyncMock(spec=EventRepository)
    mock_checkpoint_repo = AsyncMock(spec=CheckpointRepository)
    mock_stream_client = AsyncMock(spec=RedisStreamClient)

    # Setup: Execution exists in INITIALIZED state
    execution_id = UUID("00000000-0000-0000-0000-000000000001")
    mock_execution = MagicMock()
    mock_execution.id = execution_id
    mock_execution.state = ExecutionState.INITIALIZED
    mock_execution_repo.get_by_id.return_value = mock_execution

    checkpoint_manager = CheckpointManager(mock_checkpoint_repo)
    state_machine = WorkflowStateMachine()
    event_publisher = EventPublisher(mock_event_repo, mock_stream_client)

    coordinator = Coordinator(
        execution_repo=mock_execution_repo,
        event_repo=mock_event_repo,
        checkpoint_manager=checkpoint_manager,
        state_machine=state_machine,
        event_publisher=event_publisher,
    )

    await coordinator.transition_execution(execution_id, ExecutionState.ANALYZING)

    mock_execution_repo.update_state.assert_called_with(execution_id, ExecutionState.ANALYZING)
    mock_event_repo.create.assert_called_once()
    mock_stream_client.publish.assert_called_once()

@pytest.mark.asyncio
async def test_coordinator_replay_execution() -> None:
    # Mocks
    mock_execution_repo = AsyncMock(spec=ExecutionRepository)
    mock_event_repo = AsyncMock(spec=EventRepository)
    mock_checkpoint_repo = AsyncMock(spec=CheckpointRepository)
    mock_stream_client = AsyncMock(spec=RedisStreamClient)

    execution_id = UUID("00000000-0000-0000-0000-000000000001")

    # Setup checkpoint
    from storage.postgres.models.event_model import EventRecord
    from storage.postgres.models.execution_model import WorkflowCheckpoint
    from datetime import datetime, timezone

    mock_checkpoint = MagicMock(spec=WorkflowCheckpoint)
    mock_checkpoint.state = ExecutionState.INITIALIZED
    mock_checkpoint.timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    mock_checkpoint_repo.get_latest.return_value = mock_checkpoint

    # Setup events
    event1 = MagicMock(spec=EventRecord)
    event1.timestamp = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc) # Before/At checkpoint
    event1.payload_json = {"event_id": str(uuid4()), "execution_id": str(execution_id), "correlation_id": "c1", "event_type": "test1"}

    event2 = MagicMock(spec=EventRecord)
    event2.timestamp = datetime(2026, 1, 1, 0, 0, 1, tzinfo=timezone.utc) # After checkpoint
    event2.payload_json = {"event_id": str(uuid4()), "execution_id": str(execution_id), "correlation_id": "c2", "event_type": "test2"}

    mock_event_repo.get_by_execution.return_value = [event1, event2]

    checkpoint_manager = CheckpointManager(mock_checkpoint_repo)
    state_machine = WorkflowStateMachine()
    event_publisher = EventPublisher(mock_event_repo, mock_stream_client)

    coordinator = Coordinator(
        execution_repo=mock_execution_repo,
        event_repo=mock_event_repo,
        checkpoint_manager=checkpoint_manager,
        state_machine=state_machine,
        event_publisher=event_publisher,
    )

    await coordinator.replay_execution(execution_id)

    # Only event2 should be re-published
    assert mock_stream_client.publish.call_count == 1
