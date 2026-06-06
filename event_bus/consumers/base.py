import abc
from typing import Any

import structlog
from event_bus.redis_streams.client import RedisStreamClient

logger = structlog.get_logger()


class BaseEventConsumer(abc.ABC):
    def __init__(
        self,
        client: RedisStreamClient,
        stream: str,
        group_name: str,
        consumer_name: str,
    ) -> None:
        self.client = client
        self.stream = stream
        self.group_name = group_name
        self.consumer_name = consumer_name
        self._running = False

    @abc.abstractmethod
    async def process(self, event_id: str, payload: dict[str, Any]) -> None:
        """
        Process a single event from the stream.

        Args:
            event_id: The Redis stream message ID.
            payload: The event data as a dictionary.
        """
        pass

    async def run(self) -> None:
        """
        Starts the event consumption loop.
        """
        self._running = True
        await self.client.create_group(self.stream, self.group_name)

        logger.info(
            "Starting event consumer",
            stream=self.stream,
            group=self.group_name,
            consumer=self.consumer_name,
        )

        while self._running:
            try:
                events = await self.client.read_events(
                    self.stream,
                    self.group_name,
                    self.consumer_name,
                )
                for event_id, payload in events:
                    try:
                        await self.process(event_id, payload)
                        await self.client.acknowledge(
                            self.stream, self.group_name, event_id
                        )
                    except Exception as e:
                        logger.exception(
                            "Error processing event",
                            event_id=event_id,
                            error=str(e),
                        )
            except Exception as e:
                logger.exception(
                    "Error reading events from stream",
                    error=str(e),
                )

    def stop(self) -> None:
        """
        Stops the event consumption loop.
        """
        self._running = False
        logger.info("Stopping event consumer", consumer=self.consumer_name)
