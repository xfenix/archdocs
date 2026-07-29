"""Sentinel backed session storage of the showcase service."""

import typing

from redis.sentinel import Sentinel


sentinel_client: typing.Final = Sentinel([("sentinel-one", 26379), ("sentinel-two", 26379)])
sentinel_master: typing.Final = sentinel_client.master_for("orders-sessions")


def get_session_value(key: str) -> str | None:
    """Read a session value from the master behind Sentinel."""
    return sentinel_master.get(key)


def set_session_value(key: str, value: str) -> None:
    """Write a session value to the master behind Sentinel."""
    sentinel_master.set(key, value)
