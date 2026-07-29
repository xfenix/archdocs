from typing import Any

from faststream import FastStream
from faststream.nats import NatsBroker
from faststream.redis import RedisBroker


nats_broker = NatsBroker("nats://localhost:4222")
redis_broker = RedisBroker("redis://localhost:6379/2")

faststream_app = FastStream(nats_broker)


@nats_broker.subscriber("posts.created")
async def handle_created_post(event: dict[str, Any]) -> None:
    """Consume post events from NATS."""
    await redis_broker.publish(event, channel="search-index")


@redis_broker.subscriber("search-index")
async def handle_search_index(event: dict[str, Any]) -> None:
    """Consume search index events from Redis streams."""


@nats_broker.publisher("posts.indexed")
async def publish_indexed_post(event: dict[str, Any]) -> dict[str, Any]:
    """Publish an indexed post event back to NATS."""
    return event
