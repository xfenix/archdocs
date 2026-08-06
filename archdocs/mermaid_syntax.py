import dataclasses
import enum
import types
import typing

from archdocs import settings
from archdocs.diagram_model import DiagramEdge, DiagramNode, NodeGroup


_DOUBLE_QUOTE: typing.Final = '"'
_GROUP_OPENING_TEMPLATE: typing.Final = 'subgraph group_{group_name}["{group_title}"]'
_GROUP_CLOSING_LINE: typing.Final = "end"
_SERVICE_ROW_ID: typing.Final = "service_row"
_SERVICE_ROW_OPENING: typing.Final = f'subgraph {_SERVICE_ROW_ID}[" "]'
_SERVICE_ROW_DIRECTION_LINE: typing.Final = "direction LR"
_SERVICE_ROW_STYLE_LINE: typing.Final = f"style {_SERVICE_ROW_ID} fill:none,stroke:none"
_ROW_INDENT: typing.Final = settings.LINE_INDENT * 2


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


def render_node_definition(one_node: DiagramNode, /) -> str:
    return one_node.node_shape.value.format(
        defined_node_id=one_node.defined_node_id,
        node_label=one_node.node_label.replace(_DOUBLE_QUOTE, ""),
    )


def render_edge(one_edge: DiagramEdge, /) -> str:
    source_node_id: typing.Final = one_edge.source_node.defined_node_id
    target_node_id: typing.Final = one_edge.target_node.defined_node_id
    label_without_quotes: typing.Final = one_edge.edge_label.replace(_DOUBLE_QUOTE, "")
    if not label_without_quotes:
        return f"{settings.LINE_INDENT}{source_node_id} --> {target_node_id}"
    return f'{settings.LINE_INDENT}{source_node_id} --> |"{label_without_quotes}"| {target_node_id}'


# Mermaid has no coordinates: the page flows top to bottom, and a borderless row with its own
# `direction LR` turns the middle band sideways, so a group lands on the side it is written on.
@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class MermaidDiagram:
    service_node: DiagramNode
    all_edges: tuple[DiagramEdge, ...]

    def render_every_line(self) -> str:
        return "\n".join(
            (
                *self._render_definition_lines(),
                *dict.fromkeys(render_edge(one_edge) for one_edge in self.all_edges),
            ),
        )

    def _collect_drawn_nodes(self) -> tuple[DiagramNode, ...]:
        return tuple(
            {
                one_node.defined_node_id: one_node
                for one_node in (
                    self.service_node,
                    *(
                        one_edge_end
                        for one_edge in self.all_edges
                        for one_edge_end in (one_edge.source_node, one_edge.target_node)
                    ),
                )
            }.values(),
        )

    def _render_group_lines(
        self,
        node_group: NodeGroup,
        all_nodes: tuple[DiagramNode, ...],
        group_shift: str,
        /,
    ) -> tuple[str, ...]:
        grouped_nodes: typing.Final = tuple(one_node for one_node in all_nodes if one_node.node_group is node_group)
        if not grouped_nodes:
            return ()
        return (
            group_shift + _GROUP_OPENING_TEMPLATE.format(group_name=node_group.name, group_title=node_group.value),
            *(group_shift + settings.LINE_INDENT + render_node_definition(one_node) for one_node in grouped_nodes),
            group_shift + _GROUP_CLOSING_LINE,
        )

    def _render_placement_lines(
        self,
        group_placement: GroupPlacement,
        all_nodes: tuple[DiagramNode, ...],
        group_shift: str,
        /,
    ) -> tuple[str, ...]:
        return tuple(
            one_group_line
            for one_node_group in NodeGroup
            if PLACEMENT_OF_NODE_GROUP[one_node_group] is group_placement
            for one_group_line in self._render_group_lines(one_node_group, all_nodes, group_shift)
        )

    def _render_service_row_lines(self, all_nodes: tuple[DiagramNode, ...], /) -> tuple[str, ...]:
        sideways_lines: typing.Final = (
            *self._render_placement_lines(GroupPlacement.left_of_service, all_nodes, _ROW_INDENT),
            _ROW_INDENT + render_node_definition(self.service_node),
            *self._render_placement_lines(GroupPlacement.right_of_service, all_nodes, _ROW_INDENT),
        )
        return (
            settings.LINE_INDENT + _SERVICE_ROW_OPENING,
            _ROW_INDENT + _SERVICE_ROW_DIRECTION_LINE,
            *sideways_lines,
            settings.LINE_INDENT + _GROUP_CLOSING_LINE,
            settings.LINE_INDENT + _SERVICE_ROW_STYLE_LINE,
        )

    def _render_definition_lines(self) -> tuple[str, ...]:
        all_nodes: typing.Final = self._collect_drawn_nodes()
        return (
            *(
                settings.LINE_INDENT + render_node_definition(one_node)
                for one_node in all_nodes
                if one_node.node_group is None and one_node.defined_node_id != self.service_node.defined_node_id
            ),
            *self._render_placement_lines(GroupPlacement.above_service, all_nodes, settings.LINE_INDENT),
            *self._render_service_row_lines(all_nodes),
            *self._render_placement_lines(GroupPlacement.below_service, all_nodes, settings.LINE_INDENT),
        )
