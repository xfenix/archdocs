import dataclasses
import enum
import typing


@typing.final
class HttpClientEnum(enum.Enum):
    httpx = "httpx"
    aiohttp = "aiohttp"
    requests = "requests"
    niquests = "niquests"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HttpClientFeatures:
    clients_used: frozenset[str]
    async_used: bool
    has_external_calls: bool
