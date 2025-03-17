import dataclasses
import typing


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class RedisFeatures:
    connection_type: str | None
    async_used: bool
    retry_used: bool
