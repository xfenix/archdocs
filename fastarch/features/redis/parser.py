import re as py_re
import typing

from fastarch import settings
from fastarch.features.redis.const import RedisFeatures


_REDIS_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+redis\b|import\s+redis\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_ASYNC_REDIS_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+redis\.asyncio\b|import\s+redis\.asyncio\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_REDIS_CONNECTION_PATTERNS: typing.Final[dict[str, py_re.Pattern]] = {
    "plain": py_re.compile(r"\b(?:redis\.|from\s+redis\s+import\s+).*\bRedis\b", flags=settings.TYPICAL_RE_FLAGS),
    "sentinel": py_re.compile(
        r"\b(?:redis\.sentinel\.|from\s+redis(?:\.sentinel)?\s+import\s+).*\bSentinel\b",
        flags=settings.TYPICAL_RE_FLAGS,
    ),
    "cluster": py_re.compile(
        r"\b(?:redis\.cluster\.|from\s+redis(?:\.cluster)?\s+import\s+).*\bRedisCluster\b",
        flags=settings.TYPICAL_RE_FLAGS,
    ),
}
_REDIS_RETRY_PATTERN: typing.Final = py_re.compile(
    r"\bredis\.Retry\s*\(",
    flags=settings.TYPICAL_RE_FLAGS,
)


def find_redis_features(raw_source: str) -> RedisFeatures:
    if not _REDIS_IMPORT_PATTERN.search(raw_source):
        return RedisFeatures(cluster_or_sentinel=False, connection_type=None, async_used=False, retry_used=False)
    connection_type: str | None = None
    for connection_type_name, pattern in _REDIS_CONNECTION_PATTERNS.items():
        if pattern.search(raw_source):
            connection_type = connection_type_name
            break
    return RedisFeatures(
        connection_type=connection_type,
        cluster_or_sentinel=connection_type in ("sentinel", "cluster"),
        async_used=bool(_ASYNC_REDIS_PATTERN.search(raw_source)),
        retry_used=bool(_REDIS_RETRY_PATTERN.search(raw_source)),
    )
