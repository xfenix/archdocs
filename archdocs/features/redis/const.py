import dataclasses
import typing


type RedisConnectionKind = typing.Literal["sentinel", "cluster", "plain"]


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class RedisFeatures:
    connection_type: RedisConnectionKind | None
    cluster_or_sentinel: bool
    async_used: bool
    retry_used: bool
