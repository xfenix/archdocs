import re as py_re
import types
import typing

from archdocs import prefilter, settings
from archdocs.features.redis.const import RedisConnectionKind, RedisFeatures


_REDIS_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+redis\b|import\s+redis\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_ASYNC_REDIS_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+redis\.asyncio\b|import\s+redis\.asyncio\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
type _ConnectionPatterns = types.MappingProxyType[RedisConnectionKind, py_re.Pattern[str]]

# Declaration order is probing order, so the specific kinds go before plain: a file importing
# both a Sentinel and a plain Redis client is drawn by the topology, not by the fallback.
_REDIS_CONNECTION_PATTERNS: typing.Final[_ConnectionPatterns] = types.MappingProxyType(
    {
        "sentinel": py_re.compile(
            r"\b(?:redis\.(?:asyncio\.)?sentinel\.|from\s+redis(?:\.asyncio)?(?:\.sentinel)?\s+import\s+)"
            r".*\bSentinel\b",
            flags=settings.TYPICAL_RE_FLAGS,
        ),
        "cluster": py_re.compile(
            r"\b(?:redis\.(?:asyncio\.)?cluster\.|from\s+redis(?:\.asyncio)?(?:\.cluster)?\s+import\s+)"
            r".*\bRedisCluster\b",
            flags=settings.TYPICAL_RE_FLAGS,
        ),
        "plain": py_re.compile(r"\b(?:redis\.|from\s+redis\s+import\s+).*\bRedis\b", flags=settings.TYPICAL_RE_FLAGS),
    },
)
_REDIS_RETRY_PATTERN: typing.Final = py_re.compile(
    r"\bredis\.Retry\s*\(",
    flags=settings.TYPICAL_RE_FLAGS,
)
_EMPTY_FEATURES: typing.Final = RedisFeatures(
    cluster_or_sentinel=False,
    connection_type=None,
    async_used=False,
    retry_used=False,
)


def find_redis_features(raw_source: str) -> RedisFeatures:
    if not prefilter.contains_any_literal(raw_source.lower(), ("redis",)):
        return _EMPTY_FEATURES
    if not _REDIS_IMPORT_PATTERN.search(raw_source):
        return _EMPTY_FEATURES
    connection_type: typing.Final = next(
        (one_type_name for one_type_name, pattern in _REDIS_CONNECTION_PATTERNS.items() if pattern.search(raw_source)),
        None,
    )
    return RedisFeatures(
        connection_type=connection_type,
        cluster_or_sentinel=connection_type in ("sentinel", "cluster"),
        async_used=bool(_ASYNC_REDIS_PATTERN.search(raw_source)),
        retry_used=bool(_REDIS_RETRY_PATTERN.search(raw_source)),
    )
