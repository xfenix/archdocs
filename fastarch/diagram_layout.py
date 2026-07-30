import enum
import types
import typing

from fastarch import mermaid_syntax, settings
from fastarch.diagram_model import DiagramEdge, DiagramNode, NodeGroup


# Mermaid places nodes by arrow direction alone, so the four sides of the service are earned,
# not set: the page flows top to bottom, which puts whatever feeds the service above it and
# whatever it writes to below it, and a borderless wrapper turns the middle band sideways so
# callers sit left of the service and everything it calls sits right of it.
@typing.final
class GroupPlacement(enum.Enum):
    above_service = "above"
    left_of_service = "left"
    right_of_service = "right"
    below_service = "below"


PLACEMENT_OF_NODE_GROUP: typing.Final = types.MappingProxyType(
    {
        NodeGroup.configuration: GroupPlacement.above_service,
        NodeGroup.inbound_api: GroupPlacement.left_of_service,
        NodeGroup.messaging_and_tasks: GroupPlacement.right_of_service,
        NodeGroup.outbound_calls: GroupPlacement.right_of_service,
        NodeGroup.data_stores: GroupPlacement.below_service,
    },
)
_GROUP_OPENING_TEMPLATE: typing.Final = 'subgraph group_{group_name}["{group_title}"]'
_GROUP_CLOSING_LINE: typing.Final = "end"
_SERVICE_ROW_ID: typing.Final = "service_row"
_SERVICE_ROW_OPENING: typing.Final = f'subgraph {_SERVICE_ROW_ID}[" "]'
_SERVICE_ROW_DIRECTION_LINE: typing.Final = "direction LR"
_SERVICE_ROW_STYLE_LINE: typing.Final = f"style {_SERVICE_ROW_ID} fill:none,stroke:none"


def render_deeper_lines(all_lines: typing.Iterable[str], /) -> tuple[str, ...]:
    return tuple(settings.SHIFT_LEFT + one_line for one_line in all_lines)


def _render_group_lines(node_group: NodeGroup, all_nodes: tuple[DiagramNode, ...], /) -> tuple[str, ...]:
    grouped_nodes: typing.Final = tuple(one_node for one_node in all_nodes if one_node.node_group is node_group)
    if not grouped_nodes:
        return ()
    return (
        settings.SHIFT_LEFT + _GROUP_OPENING_TEMPLATE.format(group_name=node_group.name, group_title=node_group.value),
        *render_deeper_lines(mermaid_syntax.render_node_definition(one_node) for one_node in grouped_nodes),
        settings.SHIFT_LEFT + _GROUP_CLOSING_LINE,
    )


def render_placement_lines(group_placement: GroupPlacement, all_nodes: tuple[DiagramNode, ...], /) -> tuple[str, ...]:
    return tuple(
        one_group_line
        for one_node_group in NodeGroup
        if PLACEMENT_OF_NODE_GROUP[one_node_group] is group_placement
        for one_group_line in _render_group_lines(one_node_group, all_nodes)
    )


def _render_service_row_lines(service_node: DiagramNode, all_nodes: tuple[DiagramNode, ...], /) -> tuple[str, ...]:
    sideways_lines: typing.Final = (
        *render_deeper_lines(render_placement_lines(GroupPlacement.left_of_service, all_nodes)),
        settings.SHIFT_LEFT + mermaid_syntax.render_node_definition(service_node),
        *render_deeper_lines(render_placement_lines(GroupPlacement.right_of_service, all_nodes)),
    )
    return (
        settings.SHIFT_LEFT + _SERVICE_ROW_OPENING,
        settings.SHIFT_LEFT * 2 + _SERVICE_ROW_DIRECTION_LINE,
        *sideways_lines,
        settings.SHIFT_LEFT + _GROUP_CLOSING_LINE,
        settings.SHIFT_LEFT + _SERVICE_ROW_STYLE_LINE,
    )


def _collect_drawn_nodes(
    service_node: DiagramNode,
    all_edges: tuple[DiagramEdge, ...],
    /,
) -> tuple[DiagramNode, ...]:
    return tuple(
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


def render_definition_lines(service_node: DiagramNode, all_edges: tuple[DiagramEdge, ...], /) -> tuple[str, ...]:
    all_nodes: typing.Final = _collect_drawn_nodes(service_node, all_edges)
    return (
        *(
            mermaid_syntax.render_node_definition(one_node)
            for one_node in all_nodes
            if one_node.node_group is None and one_node.defined_node_id != service_node.defined_node_id
        ),
        *render_placement_lines(GroupPlacement.above_service, all_nodes),
        *_render_service_row_lines(service_node, all_nodes),
        *render_placement_lines(GroupPlacement.below_service, all_nodes),
    )
