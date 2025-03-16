import dataclasses
import re as py_re
import typing

from experimental.fastarch import settings


_REDIS_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+redis\b|import\s+redis\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_ASYNC_REDIS_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+redis\.asyncio\b|import\s+redis\.asyncio\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_REDIS_CONNECTION_PATTERNS: typing.Final[dict[str, py_re.Pattern]] = {
    "plain": py_re.compile(r"\bredis\.Redis\s*\(", flags=settings.TYPICAL_RE_FLAGS),
    "sentinel": py_re.compile(r"\bredis\.sentinel\.Sentinel\s*\(", flags=settings.TYPICAL_RE_FLAGS),
    "cluster": py_re.compile(r"\bredis\.cluster\.RedisCluster\s*\(", flags=settings.TYPICAL_RE_FLAGS),
}


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class RedisFeatures:
    connection_type: str | None
    async_used: bool


def find_redis_features(raw_source: str) -> RedisFeatures:
    if not _REDIS_IMPORT_PATTERN.search(raw_source):
        return RedisFeatures(connection_type=None, async_used=False, redis_used=False)
    connection_type: str
    for connection_type_name, pattern in _REDIS_CONNECTION_PATTERNS.items():
        if pattern.search(raw_source):
            connection_type = connection_type_name
            break
    else:
        connection_type = None
    return RedisFeatures(
        connection_type=connection_type,
        async_used=bool(_ASYNC_REDIS_PATTERN.search(raw_source)),
    )
