import ast
import re as py_re
import typing

from archdocs import prefilter, settings, syntax_tree
from archdocs.features.sqlalchemy.const import SQLAlchemyFeatures


_ENGINE_FACTORY_NAMES: typing.Final = frozenset(("create_engine", "create_async_engine"))
_ASYNC_ENGINE_MODULE: typing.Final = "sqlalchemy.ext.asyncio"
_POOL_ARGUMENT_PREFIX: typing.Final = "pool_"
_SESSION_ATTRS_NAME: typing.Final = "target_session_attrs"
# Inside a string the attribute is a `key=value` pair of a dsn query or of libpq options; outside
# of one it is an assignment, a keyword or a dict key, and those the syntax tree spells out itself.
_SESSION_ATTRS_IN_STRING_PATTERN: typing.Final = py_re.compile(
    r"target_session_attrs\s*=\s*(?P<attrs_value>[\w-]+)",
    settings.TYPICAL_RE_FLAGS,
)
_DSN_HOSTS_PATTERN: typing.Final = py_re.compile(r"://(?:[^/@]*@)?(?P<dsn_hosts>[^/]*)", settings.TYPICAL_RE_FLAGS)
_DATABASE_SCHEME_PATTERN: typing.Final = py_re.compile(
    r"(?:postgresql|mysql|sqlite|oracle|mssql|mariadb|cockroachdb)(?:\+.*)?",
    settings.TYPICAL_RE_FLAGS,
)
# One union of literals for the whole feature: an engine is found not only by the package
# name but by a bare DSN in a string, so the database schemes of `_DATABASE_SCHEME_PATTERN` belong here too.
_SQLALCHEMY_LITERALS: typing.Final = (
    "sqlalchemy",
    "create_engine",
    "create_async_engine",
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


def _read_engine_hosts(engine_call: ast.Call) -> str:
    match engine_call.args:
        case [ast.Constant(value=str() as engine_dsn), *_]:
            hosts_match: typing.Final = _DSN_HOSTS_PATTERN.search(engine_dsn)
            return hosts_match.group("dsn_hosts") if hosts_match else ""
        case _:
            return ""


def _read_named_string_values(one_node: ast.AST) -> tuple[tuple[str, str], ...]:
    match one_node:
        case ast.Assign(targets=every_target, value=ast.Constant(value=str() as assigned_value)):
            return tuple(
                (one_target.id, assigned_value) for one_target in every_target if isinstance(one_target, ast.Name)
            )
        case ast.AnnAssign(target=ast.Name(id=assigned_name), value=ast.Constant(value=str() as assigned_value)):
            return ((assigned_name, assigned_value),)
        case ast.keyword(arg=str() as keyword_name, value=ast.Constant(value=str() as keyword_value)):
            return ((keyword_name, keyword_value),)
        case ast.Dict(keys=every_key, values=every_value):
            return tuple(
                (dict_key.value, dict_value.value)
                for dict_key, dict_value in zip(every_key, every_value, strict=True)
                if isinstance(dict_key, ast.Constant)
                and isinstance(dict_key.value, str)
                and isinstance(dict_value, ast.Constant)
                and isinstance(dict_value.value, str)
            )
        case _:
            return ()


def _read_session_attrs(one_node: ast.AST) -> str:
    if isinstance(one_node, ast.Constant) and isinstance(one_node.value, str):
        string_match: typing.Final = _SESSION_ATTRS_IN_STRING_PATTERN.search(one_node.value)
        return string_match.group("attrs_value") if string_match else ""
    return next(
        (
            one_value
            for one_name, one_value in _read_named_string_values(one_node)
            if one_name.lower() == _SESSION_ATTRS_NAME
        ),
        "",
    )


def _read_database_type(one_node: ast.AST) -> str:
    match one_node:
        case ast.Constant(value=str() as string_value) if _DATABASE_SCHEME_PATTERN.fullmatch(string_value):
            return string_value
        case _:
            return ""


def find_sqlalchemy_features(raw_source: str) -> SQLAlchemyFeatures:
    if not prefilter.contains_any_literal(raw_source.lower(), _SQLALCHEMY_LITERALS):
        return _EMPTY_FEATURES
    # A python 2 leftover or a template that only looks like python costs that one file its
    # databases: the rest of the project is still drawn.
    parsed_tree: typing.Final = syntax_tree.parse_syntax_tree(raw_source)
    if parsed_tree is None:
        return _EMPTY_FEATURES
    every_node: typing.Final = syntax_tree.list_nodes_in_source_order(parsed_tree)
    engine_calls: typing.Final = [
        one_node
        for one_node in every_node
        if isinstance(one_node, ast.Call) and syntax_tree.read_callee_name(one_node) in _ENGINE_FACTORY_NAMES
    ]
    return SQLAlchemyFeatures(
        async_used=any(
            one_module.startswith(_ASYNC_ENGINE_MODULE)
            for one_node in every_node
            for one_module in syntax_tree.read_imported_modules(one_node)
        ),
        pooling_used=any(
            (one_keyword.arg or "").startswith(_POOL_ARGUMENT_PREFIX)
            for one_call in engine_calls
            for one_keyword in one_call.keywords
        ),
        multiple_hosts=any("," in _read_engine_hosts(one_call) for one_call in engine_calls),
        target_session_attrs=next(filter(None, map(_read_session_attrs, every_node)), ""),
        database_type=next(filter(None, map(_read_database_type, every_node)), ""),
    )
