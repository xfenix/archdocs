"""Redis cache configuration."""

import typing

import redis
from redis.backoff import ExponentialBackoff


redis_client: typing.Final = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
    retry=redis.Retry(ExponentialBackoff(), 3),
)


async def get_cached_value(key: str) -> str | None:
    """Get value from Redis cache."""
    return redis_client.get(key)


async def set_cached_value(key: str, value: str) -> None:
    """Set value in Redis cache."""
    redis_client.set(key, value)
