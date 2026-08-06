import re as py_re
import types
import typing

from archdocs import prefilter, settings
from archdocs.features.http_clients.const import HTTPClientEnum, HTTPClientFeatures


_CLIENT_PATTERNS: typing.Final = types.MappingProxyType(
    {
        one_client: py_re.compile(rf"\b(?:from|import)\s+{one_client.value}\b", flags=settings.TYPICAL_RE_FLAGS)
        for one_client in HTTPClientEnum
    },
)
_ASYNC_DETECTION_PATTERN: typing.Final = py_re.compile(
    r"\b(?:httpx\.AsyncClient|aiohttp\.ClientSession)\b",
    flags=settings.TYPICAL_RE_FLAGS,
)
_EMPTY_FEATURES: typing.Final = HTTPClientFeatures(
    clients_used=frozenset(),
    async_used=False,
)


def find_http_client_features(raw_source: str) -> HTTPClientFeatures:
    lowered_source: typing.Final = raw_source.lower()
    clients_found: typing.Final = {
        one_client.value
        for one_client, one_pattern in _CLIENT_PATTERNS.items()
        if prefilter.contains_any_literal(lowered_source, (one_client.value,)) and one_pattern.search(raw_source)
    }
    if not clients_found:
        return _EMPTY_FEATURES
    return HTTPClientFeatures(
        clients_used=frozenset(clients_found),
        async_used=bool(_ASYNC_DETECTION_PATTERN.search(raw_source)),
    )
