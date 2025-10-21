"""Redis cache configuration."""

import typing

from redis import Redis
from redis.sentinel import Sentinel


redis_client: typing.Final = Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

sentinel_client: typing.Final = Sentinel([("localhost", 26379)])
sentinel_master: typing.Final = sentinel_client.master_for("mymaster")


async def get_cached_value(key: str) -> str | None:
    """Get value from Redis cache."""
    return redis_client.get(key)


async def set_cached_value(key: str, value: str) -> None:
    """Set value in Redis cache."""
    redis_client.set(key, value)
