import redis.asyncio as redis
from typing import Any


class RedisStreamClient:
    def __init__(self) -> None:
        self.client = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
        )

    async def publish(
        self,
        stream: str,
        payload: dict[str, str | int | float],
    ) -> None:
        await self.client.xadd(stream, payload)  # type: ignore

    async def create_group(
        self,
        stream: str,
        group_name: str,
    ) -> None:
        try:
            await self.client.xgroup_create(stream, group_name, id="0", mkstream=True)
        except redis.ResponseError as e:
            if "already exists" not in str(e):
                raise e

    async def read_events(
        self,
        stream: str,
        group_name: str,
        consumer_name: str,
        count: int = 10,
        block: int = 2000,
    ) -> list[tuple[str, dict[str, Any]]]:
        responses = await self.client.xreadgroup(
            group_name,
            consumer_name,
            {stream: ">"},
            count=count,
            block=block,
        )

        events = []
        for stream_res, messages in responses:
            for message_id, payload in messages:
                events.append((message_id, payload))

        return events

    async def acknowledge(
        self,
        stream: str,
        group_name: str,
        message_id: str,
    ) -> None:
        await self.client.xack(stream, group_name, message_id)
