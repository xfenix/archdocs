"""Redis connections of the showcase service."""

import typing

import redis
import redis.asyncio
from redis.backoff import ExponentialBackoff


RETRY_POLICY: typing.Final = redis.Retry(ExponentialBackoff(), 3)

cache_client: typing.Final = redis.asyncio.Redis(
    host="cache.internal",
    port=6379,
    db=0,
    decode_responses=True,
    retry=RETRY_POLICY,
)
queue_connection: typing.Final = redis.Redis(host="cache.internal", port=6379, db=3, retry=RETRY_POLICY)


async def get_cached_order(order_id: int) -> str | None:
    """Read an order from the cache."""
    return await cache_client.get(f"order:{order_id}")


async def set_cached_order(order_id: int, payload: str) -> None:
    """Put an order into the cache."""
    await cache_client.set(f"order:{order_id}", payload)
