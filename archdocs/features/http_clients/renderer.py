import typing

from archdocs import diagram_model
from archdocs.features.http_clients.const import HttpClientFeatures


def render_http_client_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: HttpClientFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if not features_to_draw.clients_used:
        return ()

    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                "async" if features_to_draw.async_used else "",
                ", ".join(sorted(features_to_draw.clients_used)),
            ],
        ),
    )

    return (
        diagram_model.DiagramEdge(
            source_node=service_node,
            target_node=diagram_model.EXTERNAL_API_NODE,
            edge_label=f"HTTP ({properties_on_arrow})",
        ),
    )
