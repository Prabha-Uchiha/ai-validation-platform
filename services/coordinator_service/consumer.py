from typing import Any
from uuid import UUID

import structlog
from opentelemetry import trace
from event_bus.consumers.base import BaseEventConsumer
from event_bus.redis_streams.client import RedisStreamClient
from event_bus.schemas.stream_events import StreamName
from platform_core.schemas.execution import ExecutionState
from storage.postgres.database import async_session_maker
from storage.postgres.repositories.execution_repo import ExecutionRepository
from storage.postgres.repositories.checkpoint_repo import CheckpointRepository
from storage.postgres.repositories.event_repo import EventRepository
from services.coordinator_service.checkpoints import CheckpointManager
from services.coordinator_service.state_machine import WorkflowStateMachine
from services.coordinator_service.coordinator import Coordinator
from event_bus.publishers.publisher import EventPublisher

logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

class CoordinatorConsumer(BaseEventConsumer):
    def __init__(
        self,
        client: RedisStreamClient,
        state_machine: WorkflowStateMachine,
    ) -> None:
        super().__init__(
            client=client,
            stream=StreamName.EXECUTION_EVENTS,
            group_name="coordinator_group",
            consumer_name="coordinator_consumer_1",
        )
        self.state_machine = state_machine

    async def process(self, event_id: str, payload: dict[str, Any]) -> None:
        event_type = payload.get("event_type")
        execution_id_str = payload.get("execution_id")
        correlation_id = payload.get("correlation_id")

        if not event_type or not execution_id_str:
            logger.warn("Event missing required fields", event_id=event_id)
            return

        try:
            execution_id = UUID(execution_id_str)
        except ValueError:
            logger.error("Invalid execution_id in event", event_id=event_id, execution_id_str=execution_id_str)
            return

        with tracer.start_as_current_span(
            "process_event",
            attributes={
                "event_type": event_type,
                "execution_id": str(execution_id),
                "correlation_id": correlation_id or "unknown",
            },
        ):
            logger.info("Processing event", event_type=event_type, execution_id=execution_id, correlation_id=correlation_id)

            if event_type == "execution.started":
                # Automatically transition to ANALYZING to start the workflow
                await self._transition_to_analyzing(execution_id, correlation_id)

    async def _transition_to_analyzing(self, execution_id: UUID, correlation_id: str | None) -> None:
        async with async_session_maker() as session:
            execution_repo = ExecutionRepository(session)
            checkpoint_repo = CheckpointRepository(session)
            event_repo = EventRepository(session)
            checkpoint_manager = CheckpointManager(checkpoint_repo)

            event_publisher = EventPublisher(event_repo, self.client)

            coordinator = Coordinator(
                execution_repo=execution_repo,
                event_repo=event_repo,
                checkpoint_manager=checkpoint_manager,
                state_machine=self.state_machine,
                event_publisher=event_publisher,
            )

            try:
                await coordinator.transition_execution(
                    execution_id=execution_id,
                    target_state=ExecutionState.ANALYZING,
                    metadata={"auto_transition": True, "correlation_id": correlation_id},
                )
                logger.info("Automatically transitioned to ANALYZING", execution_id=execution_id, correlation_id=correlation_id)
            except Exception as e:
                logger.exception(
                    "Failed to automate transition to ANALYZING",
                    execution_id=execution_id,
                    correlation_id=correlation_id,
                    error=str(e),
                )
