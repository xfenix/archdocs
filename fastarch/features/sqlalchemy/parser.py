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
    _target_session_attrs_match: typing.Final = _TARGET_SESSION_ATTRS_PATTERN.search(raw_source)
    _database_type_match: typing.Final = _DB_TYPE_PATTERN.search(raw_source)
    return SQLAlchemyFeatures(
        async_used=_ASYNC_ENGINE_PATTERN.search(raw_source) is not None,
        pooling_used=_POOLING_PATTERN.search(raw_source) is not None,
        multiple_hosts=_MULTIPLE_HOSTS_PATTERN.search(raw_source) is not None,
        target_session_attrs=_target_session_attrs_match.group(1) if _target_session_attrs_match else "",
        database_type=_database_type_match.group(1) if _database_type_match else "",
    )
