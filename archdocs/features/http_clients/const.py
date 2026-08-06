import dataclasses
import enum
import typing


@typing.final
class HttpClientEnum(enum.Enum):
    httpx_client = "httpx"
    aiohttp_client = "aiohttp"
    requests_client = "requests"
    niquests_client = "niquests"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HttpClientFeatures:
    clients_used: frozenset[str]
    async_used: bool
