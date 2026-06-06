from datetime import datetime, timezone
from uuid import uuid4, UUID
from typing import Any

import structlog
from opentelemetry import trace
from platform_core.schemas.execution import ExecutionState
from platform_core.contracts.events import ExecutionStarted, StateTransitioned
from platform_core.observability.correlation import generate_correlation_id
from storage.postgres.repositories.execution_repo import ExecutionRepository
from storage.postgres.repositories.event_repo import EventRepository
from services.coordinator_service.checkpoints import CheckpointManager
from services.coordinator_service.state_machine import WorkflowStateMachine
from event_bus.publishers.publisher import EventPublisher
from event_bus.schemas.stream_events import StreamName

logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

class Coordinator:
    def __init__(
        self,
        execution_repo: ExecutionRepository,
        event_repo: EventRepository,
        checkpoint_manager: CheckpointManager,
        state_machine: WorkflowStateMachine,
        event_publisher: EventPublisher,
    ) -> None:
        self.execution_repo = execution_repo
        self.event_repo = event_repo
        self.checkpoint_manager = checkpoint_manager
        self.state_machine = state_machine
        self.event_publisher = event_publisher

    async def start_execution(self, repository_url: str, branch: str) -> UUID:
        with tracer.start_as_current_span(
            "start_execution",
            attributes={"repository_url": repository_url, "branch": branch},
        ) as span:
            execution_id = uuid4()
            correlation_id = generate_correlation_id()

            span.set_attribute("execution_id", str(execution_id))
            span.set_attribute("correlation_id", correlation_id)

            # 1. Persist execution
            await self.execution_repo.create(
                execution_id=execution_id,
                repository_url=repository_url,
                state=ExecutionState.INITIALIZED,
            )

            # 2. Create initial checkpoint
            await self.checkpoint_manager.create_checkpoint(
                execution_id=execution_id,
                state=ExecutionState.INITIALIZED,
                metadata={"branch": branch, "correlation_id": correlation_id},
            )

            # 3. Emit ExecutionStarted event
            event = ExecutionStarted(
                event_id=uuid4(),
                execution_id=execution_id,
                timestamp=datetime.now(timezone.utc),
                event_type="execution.started",
                correlation_id=correlation_id,
                repository_url=repository_url,
            )

            await self.event_publisher.publish(
                StreamName.EXECUTION_EVENTS,
                event,
            )

            logger.info(
                "Execution started",
                execution_id=execution_id,
                repository_url=repository_url,
                correlation_id=correlation_id
            )
            return execution_id

    async def transition_execution(
        self,
        execution_id: UUID,
        target_state: ExecutionState,
        metadata: dict[str, Any] | None = None
    ) -> None:
        with tracer.start_as_current_span(
            "transition_execution",
            attributes={"execution_id": str(execution_id), "target_state": target_state.value},
        ) as span:
            # 1. Get current state
            execution = await self.execution_repo.get_by_id(execution_id)
            if not execution:
                raise ValueError(f"Execution {execution_id} not found")

            current_state = execution.state
            correlation_id = generate_correlation_id()

            span.set_attribute("correlation_id", correlation_id)

            # 2. Validate transition
            new_state = self.state_machine.transition(current_state, target_state)

            # 3. Update state in DB
            await self.execution_repo.update_state(execution_id, new_state)

            # 4. Create checkpoint
            await self.checkpoint_manager.create_checkpoint(
                execution_id=execution_id,
                state=new_state,
                metadata=metadata or {},
            )

            # 5. Emit StateTransitioned event
            event = StateTransitioned(
                event_id=uuid4(),
                execution_id=execution_id,
                timestamp=datetime.now(timezone.utc),
                event_type="execution.state_transitioned",
                correlation_id=correlation_id,
                from_state=current_state.value,
                to_state=new_state.value,
            )

            await self.event_publisher.publish(
                StreamName.EXECUTION_EVENTS,
                event,
            )

            logger.info(
                "Execution transitioned",
                execution_id=execution_id,
                from_state=current_state,
                to_state=new_state,
                correlation_id=correlation_id
            )

    async def replay_execution(self, execution_id: UUID) -> None:
        """
        Replays the execution from the last known checkpoint.
        """
        with tracer.start_as_current_span(
            "replay_execution",
            attributes={"execution_id": str(execution_id)},
        ) as span:
            correlation_id = generate_correlation_id()
            span.set_attribute("correlation_id", correlation_id)

            # 1. Find the latest checkpoint
            checkpoint = await self.checkpoint_manager.get_latest_checkpoint(execution_id)
            if not checkpoint:
                raise ValueError(f"No checkpoint found for execution {execution_id}")

            logger.info(
                "Replaying execution from last checkpoint",
                execution_id=execution_id,
                state=checkpoint.state,
                timestamp=checkpoint.timestamp,
                correlation_id=correlation_id
            )

            # 2. Fetch all events that occurred after the checkpoint
            events = await self.event_repo.get_by_execution(execution_id)

            # Filter events that happened after the checkpoint timestamp
            events_to_replay = [
                e for e in events if e.timestamp > checkpoint.timestamp
            ]

            logger.info(
                "Found events to replay",
                execution_id=execution_id,
                count=len(events_to_replay),
                correlation_id=correlation_id
            )

            # 3. Re-emit these events to the bus to trigger the workflow again
            # In a real replay, we might want to mark these as 'replayed'
            # or use a special replay stream.
            for event_record in events_to_replay:
                # We rebuild the Event model from the persisted payload
                # For simplicity, we just use the payload as it was
                await self.event_publisher.publish(
                    StreamName.EXECUTION_EVENTS,
                    event_record.payload_json # This needs to be a Pydantic Event,
                                             # but for now we can adjust publisher to handle dicts
                )
