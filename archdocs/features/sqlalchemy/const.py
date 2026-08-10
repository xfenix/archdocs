import dataclasses
import typing


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class SQLAlchemyFeatures:
    async_used: bool
    pooling_used: bool
    multiple_hosts: bool
    target_session_attrs: str = ""
    database_type: str = ""
