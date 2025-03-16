import dataclasses


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class SQLAlchemyFeatures:
    async_used: bool
    pooling_used: bool
    multiple_hosts: bool
    # https://magicstack.github.io/asyncpg/current/api/index.html more info about them
    target_session_attrs: str | None
    database_type: str | None
