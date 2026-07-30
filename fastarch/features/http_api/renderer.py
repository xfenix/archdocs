import typing

from fastarch import diagram_model
from fastarch.features.http_api.const import HTTPApiFeatures


def render_http_api_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: HTTPApiFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if not features_to_draw.in_methods_existed and not features_to_draw.out_methods_existed:
        return ()
    all_edges: typing.Final[list[diagram_model.DiagramEdge]] = []
    if features_to_draw.in_methods_existed:
        in_methods: typing.Final = ", ".join(sorted(features_to_draw.in_methods))
        all_edges.append(
            diagram_model.DiagramEdge(
                source_node=diagram_model.EXTERNAL_CLIENT_NODE,
                target_node=service_node,
                edge_label=f"REST ({in_methods});",
            ),
        )
    if features_to_draw.out_methods_existed:
        out_methods: typing.Final = ", ".join(sorted(features_to_draw.out_methods))
        all_edges.append(
            diagram_model.DiagramEdge(
                source_node=service_node,
                target_node=diagram_model.EXTERNAL_CLIENT_NODE,
                edge_label=f"REST ({out_methods});",
            ),
        )
    return tuple(all_edges)
