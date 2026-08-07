import typing

from archdocs import diagram_model
from archdocs.features.http_api.const import HTTPApiFeatures


def render_http_api_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: HTTPApiFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if not features_to_draw.served_methods:
        return ()
    served_methods: typing.Final = ", ".join(sorted(features_to_draw.served_methods))
    return (
        diagram_model.DiagramEdge(
            source_node=diagram_model.EXTERNAL_CLIENT_NODE,
            target_node=service_node,
            edge_label=f"REST ({served_methods})",
        ),
    )
