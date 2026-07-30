import typing

from fastarch import settings
from fastarch.diagram_model import DiagramEdge, DiagramNode, build_service_node


_DOUBLE_QUOTE: typing.Final = '"'


def render_service_node_id(service_name: str) -> str:
    return build_service_node(service_name).defined_node_id


def render_edge_label(raw_label: str) -> str:
    return f'|"{raw_label.replace(_DOUBLE_QUOTE, "")}"|'


def render_edge(one_edge: DiagramEdge, /) -> str:
    source_node_id: typing.Final = one_edge.source_node.defined_node_id
    target_node_id: typing.Final = one_edge.target_node.defined_node_id
    if not one_edge.edge_label:
        return f"{settings.SHIFT_LEFT}{source_node_id} --> {target_node_id}"
    return f"{settings.SHIFT_LEFT}{source_node_id} --> {render_edge_label(one_edge.edge_label)} {target_node_id}"


def render_node_definition(one_node: DiagramNode, /) -> str:
    return settings.SHIFT_LEFT + one_node.node_shape.value.format(
        defined_node_id=one_node.defined_node_id,
        node_label=one_node.node_label.replace(_DOUBLE_QUOTE, ""),
    )


def render_service_node_definition(service_name: str, node_annotations: typing.Iterable[str] = ()) -> str:
    return render_node_definition(build_service_node(service_name, node_annotations))
