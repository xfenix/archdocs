import re as py_re
import typing

from fastarch import mermaid_syntax, settings
from fastarch.features.sqlalchemy.const import SQLAlchemyFeatures


# The parser captures the whole quoted dsn, which routinely carries userinfo. That must
# never reach the served page, so every `://<userinfo>@` is masked before it is drawn,
# including the colon free `://token@host` form.
_DSN_CREDENTIALS_PATTERN: typing.Final = py_re.compile(r"://[^/@\s]*@", flags=settings.TYPICAL_RE_FLAGS)
_DSN_SCHEME_PATTERN: typing.Final = py_re.compile(r"^[^:/\s]+", flags=settings.TYPICAL_RE_FLAGS)


def _render_masked_dsn(raw_database_type: str) -> str:
    return _DSN_CREDENTIALS_PATTERN.sub("://***@", raw_database_type)


def _render_database_node_id(raw_database_type: str, host_suffix: int | str) -> str:
    scheme_match: typing.Final = _DSN_SCHEME_PATTERN.search(raw_database_type)
    return (
        f"{mermaid_syntax.render_node_id(scheme_match.group() if scheme_match else raw_database_type)}db{host_suffix}"
    )


def render_sqlalchemy_features(features_to_draw: SQLAlchemyFeatures) -> str:
    if not features_to_draw.database_type:
        return ""
    diagram_parts: typing.Final[list[str]] = []
    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                "async" if features_to_draw.async_used else "",
                _render_masked_dsn(features_to_draw.database_type),
                features_to_draw.target_session_attrs,
            ],
        ),
    )
    connections_number: typing.Final = (
        settings.VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION if features_to_draw.pooling_used else 1
    )
    for one_counter in range(connections_number):
        host_suffix = one_counter if features_to_draw.multiple_hosts else ""
        diagram_parts.append(
            mermaid_syntax.render_edge(
                settings.SERVICE_NODE_ID,
                properties_on_arrow,
                _render_database_node_id(features_to_draw.database_type, host_suffix),
            ),
        )
    return "\n".join(diagram_parts)
