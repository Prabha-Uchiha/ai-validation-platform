from uuid import UUID
from typing import Any

import structlog
from opentelemetry import trace
from platform_core.contracts.events import Event
from event_bus.redis_streams.client import RedisStreamClient
from event_bus.schemas.stream_events import StreamName
from storage.postgres.repositories.event_repo import EventRepository

logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

class EventPublisher:
    def __init__(
        self,
        event_repo: EventRepository,
        stream_client: RedisStreamClient,
    ) -> None:
        self.event_repo = event_repo
        self.stream_client = stream_client

    async def publish(
        self,
        stream: StreamName,
        event: Event | dict[str, Any],
    ) -> None:
        # Normalize to dict for persistence and publishing
        if isinstance(event, Event):
            event_id = event.event_id
            execution_id = event.execution_id
            event_type = event.event_type
            correlation_id = event.correlation_id
            payload = event.model_dump(mode="json")
        else:
            event_id = UUID(event["event_id"])
            execution_id = UUID(event["execution_id"])
            event_type = event["event_type"]
            correlation_id = event["correlation_id"]
            payload = event

        with tracer.start_as_current_span(
            f"publish_event_{event_type}",
            attributes={
                "execution_id": str(execution_id),
                "correlation_id": correlation_id,
                "event_type": event_type,
            },
        ) as span:
            try:
                # 1. Persist to Database (The source of truth for replay)
                await self.event_repo.create(
                    event_id=event_id,
                    execution_id=execution_id,
                    event_type=event_type,
                    payload=payload,
                    correlation_id=correlation_id,
                )

                # 2. Publish to Redis Stream for real-time orchestration
                await self.stream_client.publish(
                    stream.value,
                    payload,
                )

                logger.info(
                    "Event published and persisted",
                    event_type=event_type,
                    execution_id=execution_id,
                    correlation_id=correlation_id,
                )
            except Exception as e:
                span.record_exception(e)
                logger.exception(
                    "Failed to publish event",
                    event_type=event_type,
                    execution_id=execution_id,
                    error=str(e),
                )
                raise e
