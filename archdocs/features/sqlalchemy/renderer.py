import re as py_re
import typing

from archdocs import diagram_model, settings
from archdocs.features.sqlalchemy.const import SQLAlchemyFeatures


_DSN_CREDENTIALS_PATTERN: typing.Final = py_re.compile(r"://[^/@\s]*@", flags=settings.TYPICAL_RE_FLAGS)
_DSN_SCHEME_PATTERN: typing.Final = py_re.compile(r"^[^:/\s]+", flags=settings.TYPICAL_RE_FLAGS)


def _build_database_node(raw_database_type: str, node_suffix: int | str) -> diagram_model.DiagramNode:
    scheme_match: typing.Final = _DSN_SCHEME_PATTERN.search(raw_database_type)
    database_scheme: typing.Final = scheme_match.group() if scheme_match else raw_database_type
    return diagram_model.build_diagram_node(
        f"{diagram_model.render_node_id(database_scheme)}db{node_suffix}",
        database_scheme if node_suffix == "" else f"{database_scheme} #{node_suffix}",
        diagram_model.NodeGroup.data_stores,
    )


def render_sqlalchemy_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: SQLAlchemyFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if not features_to_draw.database_type:
        return ()
    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                "async" if features_to_draw.async_used else "",
                _DSN_CREDENTIALS_PATTERN.sub("://***@", features_to_draw.database_type),
                features_to_draw.target_session_attrs,
            ],
        ),
    )
    connections_number: typing.Final = (
        settings.VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION if features_to_draw.pooling_used else 1
    )
    return tuple(
        diagram_model.DiagramEdge(
            source_node=service_node,
            target_node=_build_database_node(
                features_to_draw.database_type,
                one_counter if features_to_draw.multiple_hosts else "",
            ),
            edge_label=properties_on_arrow,
        )
        for one_counter in range(connections_number)
    )
