import dataclasses
import typing


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class SQLAlchemyFeatures:
    async_used: bool
    pooling_used: bool
    multiple_hosts: bool
    database_type: str = ""
