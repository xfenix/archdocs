import typing

from fastarch import settings
from fastarch.diagram_model import DiagramEdge, DiagramNode, NodeGroup, build_service_node


_DOUBLE_QUOTE: typing.Final = '"'
_GROUP_OPENING_TEMPLATE: typing.Final = 'subgraph group_{group_name}["{group_title}"]'
_GROUP_CLOSING_LINE: typing.Final = "end"


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


def _render_group_lines(node_group: NodeGroup, all_nodes: tuple[DiagramNode, ...], /) -> tuple[str, ...]:
    grouped_nodes: typing.Final = tuple(one_node for one_node in all_nodes if one_node.node_group is node_group)
    if not grouped_nodes:
        return ()
    group_opening: typing.Final = _GROUP_OPENING_TEMPLATE.format(
        group_name=node_group.name,
        group_title=node_group.value,
    )
    return (
        settings.SHIFT_LEFT + group_opening,
        *(settings.SHIFT_LEFT + render_node_definition(one_node) for one_node in grouped_nodes),
        settings.SHIFT_LEFT + _GROUP_CLOSING_LINE,
    )


def render_definition_lines(service_node: DiagramNode, all_edges: tuple[DiagramEdge, ...], /) -> tuple[str, ...]:
    all_nodes: typing.Final = tuple(
        {
            one_node.defined_node_id: one_node
            for one_node in (
                service_node,
                *(
                    one_edge_end
                    for one_edge in all_edges
                    for one_edge_end in (one_edge.source_node, one_edge.target_node)
                ),
            )
        }.values(),
    )
    return (
        *(render_node_definition(one_node) for one_node in all_nodes if one_node.node_group is None),
        *(
            one_group_line
            for one_node_group in NodeGroup
            for one_group_line in _render_group_lines(one_node_group, all_nodes)
        ),
    )
