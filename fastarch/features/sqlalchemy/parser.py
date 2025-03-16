import re as py_re
import typing

from fastarch import settings
from fastarch.features.sqlalchemy.const import SQLAlchemyFeatures


_ASYNC_ENGINE_PATTERN: typing.Final = py_re.compile(r"sqlalchemy\.ext\.asyncio", settings.TYPICAL_RE_FLAGS)
_POOLING_PATTERN: typing.Final = py_re.compile(r"create_engine\(.+pool_", settings.TYPICAL_RE_FLAGS)
_MULTIPLE_HOSTS_PATTERN: typing.Final = py_re.compile(
    r"create_engine\([^)]*'(?:postgresql|mysql|mariadb|oracle|mssql)\+[^']*://[^/]+,[^/]+/",
    settings.TYPICAL_RE_FLAGS,
)
_TARGET_SESSION_ATTRS_PATTERN: typing.Final = py_re.compile(
    r"target_session_attrs\s*=\s*['\"](\w+)['\"]",
    settings.TYPICAL_RE_FLAGS,
)
_DB_TYPE_PATTERN: typing.Final = py_re.compile(
    r"['\"](postgresql(?:\+[^'\"]*)?|mysql(?:\+[^'\"]*)?|sqlite(?:\+[^'\"]*)?|oracle(?:\+[^'\"]*)?|"
    r"mssql(?:\+[^'\"]*)?|mariadb(?:\+[^'\"]*)?|cockroachdb(?:\+[^'\"]*)?)['\"]",
    settings.TYPICAL_RE_FLAGS,
)


def find_sqlalchemy_features(raw_source: str) -> SQLAlchemyFeatures:
    return SQLAlchemyFeatures(
        async_used=_ASYNC_ENGINE_PATTERN.search(raw_source) is not None,
        pooling_used=_POOLING_PATTERN.search(raw_source) is not None,
        multiple_hosts=_MULTIPLE_HOSTS_PATTERN.search(raw_source) is not None,
        target_session_attrs=(_TARGET_SESSION_ATTRS_PATTERN.search(raw_source) or [None]).group(1),
        database_type=(_DB_TYPE_PATTERN.search(raw_source) or [None]).group(1),
    )
