"""Sentinel backed cache configuration."""

import typing

from redis.sentinel import Sentinel


sentinel_client: typing.Final = Sentinel([("localhost", 26379), ("localhost", 26380)])
sentinel_master: typing.Final = sentinel_client.master_for("mymaster")


async def get_session_value(key: str) -> str | None:
    """Get value from the master behind Sentinel."""
    return sentinel_master.get(key)


async def set_session_value(key: str, value: str) -> None:
    """Set value on the master behind Sentinel."""
    sentinel_master.set(key, value)
