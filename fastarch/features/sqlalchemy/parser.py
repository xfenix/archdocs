import re as py_re
import typing

from fastarch import prefilter, settings
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
# One union of literals for the whole feature: an engine is found not only by the package
# name but by a bare DSN in a string, so the database schemes of `_DB_TYPE_PATTERN` belong here too.
_SQLALCHEMY_LITERALS: typing.Final = (
    "sqlalchemy",
    "create_engine",
    "target_session_attrs",
    "postgresql",
    "mysql",
    "sqlite",
    "oracle",
    "mssql",
    "mariadb",
    "cockroachdb",
)
_EMPTY_FEATURES: typing.Final = SQLAlchemyFeatures(
    async_used=False,
    pooling_used=False,
    multiple_hosts=False,
    target_session_attrs="",
    database_type="",
)


def find_sqlalchemy_features(raw_source: str) -> SQLAlchemyFeatures:
    if not prefilter.contains_any_literal(raw_source.lower(), _SQLALCHEMY_LITERALS):
        return _EMPTY_FEATURES
    target_session_attrs_match: typing.Final = _TARGET_SESSION_ATTRS_PATTERN.search(raw_source)
    database_type_match: typing.Final = _DB_TYPE_PATTERN.search(raw_source)
    return SQLAlchemyFeatures(
        async_used=_ASYNC_ENGINE_PATTERN.search(raw_source) is not None,
        pooling_used=_POOLING_PATTERN.search(raw_source) is not None,
        multiple_hosts=_MULTIPLE_HOSTS_PATTERN.search(raw_source) is not None,
        target_session_attrs=target_session_attrs_match.group(1) if target_session_attrs_match else "",
        database_type=database_type_match.group(1) if database_type_match else "",
    )
