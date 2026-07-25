import re as py_re
import types
import typing

from fastarch import settings
from fastarch.features.http_clients.const import HttpClientEnum, HttpClientFeatures


_HTTPX_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+httpx\b|import\s+httpx\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_HTTPX_ASYNC_PATTERN: typing.Final = py_re.compile(
    r"\bhttpx\.AsyncClient\b",
    flags=settings.TYPICAL_RE_FLAGS,
)
_AIOHTTP_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+aiohttp\b|import\s+aiohttp\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_REQUESTS_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+requests\b|import\s+requests\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_NIQUESTS_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+niquests\b|import\s+niquests\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)

_CLIENT_PATTERNS: typing.Final = types.MappingProxyType(
    {
        HttpClientEnum.httpx_client: _HTTPX_IMPORT_PATTERN,
        HttpClientEnum.aiohttp_client: _AIOHTTP_IMPORT_PATTERN,
        HttpClientEnum.requests_client: _REQUESTS_IMPORT_PATTERN,
        HttpClientEnum.niquests_client: _NIQUESTS_IMPORT_PATTERN,
    },
)

_ASYNC_DETECTION_PATTERNS: typing.Final = py_re.compile(
    r"\b(?:async\s+with\s+(?:httpx\.AsyncClient|aiohttp\.ClientSession)|"
    r"httpx\.AsyncClient|aiohttp\.ClientSession)\b",
    flags=settings.TYPICAL_RE_FLAGS,
)


def find_http_client_features(raw_source: str) -> HttpClientFeatures:
    clients_found: typing.Final[set[str]] = set()

    for client_enum, pattern in _CLIENT_PATTERNS.items():
        if pattern.search(raw_source):
            clients_found.add(client_enum.value)

    if not clients_found:
        return HttpClientFeatures(
            clients_used=frozenset(),
            async_used=False,
            has_external_calls=False,
        )

    async_used: typing.Final = bool(_ASYNC_DETECTION_PATTERNS.search(raw_source))

    return HttpClientFeatures(
        clients_used=frozenset(clients_found),
        async_used=async_used,
        has_external_calls=True,
    )
