import dataclasses
import enum
import re as py_re
import types
import typing

from archdocs import diagram_model, settings


DIAGRAM_HEADER: typing.Final = "graph TB"
_DOUBLE_QUOTE: typing.Final = '"'
_GROUP_OPENING_TEMPLATE: typing.Final = 'subgraph group_{group_name}["{group_title}"]'
_GROUP_CLOSING_LINE: typing.Final = "end"
_SERVICE_ROW_ID: typing.Final = "service_row"
_SERVICE_ROW_OPENING: typing.Final = f'subgraph {_SERVICE_ROW_ID}[" "]'
_SERVICE_ROW_DIRECTION_LINE: typing.Final = "direction LR"
_SERVICE_ROW_STYLE_LINE: typing.Final = f"style {_SERVICE_ROW_ID} fill:none,stroke:none"
_ROW_INDENT: typing.Final = settings.LINE_INDENT * 2
_LABEL_WHITESPACE_PATTERN: typing.Final = py_re.compile(r"\s+")


@typing.final
class GroupPlacement(enum.Enum):
    above_service = "above"
    left_of_service = "left"
    right_of_service = "right"
    below_service = "below"


PLACEMENT_OF_NODE_GROUP: typing.Final = types.MappingProxyType(
    {
        diagram_model.NodeGroup.configuration: GroupPlacement.above_service,
        diagram_model.NodeGroup.inbound_api: GroupPlacement.left_of_service,
        diagram_model.NodeGroup.messaging_and_tasks: GroupPlacement.right_of_service,
        diagram_model.NodeGroup.outbound_calls: GroupPlacement.right_of_service,
        diagram_model.NodeGroup.data_stores: GroupPlacement.below_service,
    },
)
# The templates live next to the quote-stripping below: how a shape is written in mermaid and
# what its label may contain is one piece of knowledge, and the model does not hold any of it.
_TEMPLATE_OF_NODE_SHAPE: typing.Final = types.MappingProxyType(
    {
        diagram_model.NodeShape.plain_node: '{defined_node_id}["{node_label}"]',
        diagram_model.NodeShape.service_node: '{defined_node_id}{{"{node_label}"}}',
    },
)


# A label is written inside one mermaid statement, and a statement ends at the newline: a
# service named across two lines, or a topic taken from a string that spans them, cuts the
# diagram in half and the page renders nothing. Neither end of a label is a trusted one line.
def render_label(raw_label: str, /) -> str:
    return _LABEL_WHITESPACE_PATTERN.sub(" ", raw_label.replace(_DOUBLE_QUOTE, "")).strip()


def render_node_definition(one_node: diagram_model.DiagramNode, /) -> str:
    return _TEMPLATE_OF_NODE_SHAPE[one_node.node_shape].format(
        defined_node_id=one_node.defined_node_id,
        node_label=render_label(one_node.node_label),
    )


def render_edge(one_edge: diagram_model.DiagramEdge, /) -> str:
    source_node_id: typing.Final = one_edge.source_node.defined_node_id
    target_node_id: typing.Final = one_edge.target_node.defined_node_id
    label_without_quotes: typing.Final = render_label(one_edge.edge_label)
    if not label_without_quotes:
        return f"{settings.LINE_INDENT}{source_node_id} --> {target_node_id}"
    return f'{settings.LINE_INDENT}{source_node_id} --> |"{label_without_quotes}"| {target_node_id}'


# Mermaid has no coordinates: the page flows top to bottom, and a borderless row with its own
# `direction LR` turns the middle band sideways, so a group lands on the side it is written on.
@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class MermaidDiagram:
    service_node: diagram_model.DiagramNode
    all_edges: tuple[diagram_model.DiagramEdge, ...]

    def render_every_line(self) -> str:
        return "\n".join(
            (
                *self._render_definition_lines(),
                *dict.fromkeys(render_edge(one_edge) for one_edge in self.all_edges),
            ),
        )

    def _collect_drawn_nodes(self) -> tuple[diagram_model.DiagramNode, ...]:
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
        node_group: diagram_model.NodeGroup,
        all_nodes: tuple[diagram_model.DiagramNode, ...],
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
        all_nodes: tuple[diagram_model.DiagramNode, ...],
        group_shift: str,
        /,
    ) -> tuple[str, ...]:
        return tuple(
            one_group_line
            for one_node_group in diagram_model.NodeGroup
            if PLACEMENT_OF_NODE_GROUP[one_node_group] is group_placement
            for one_group_line in self._render_group_lines(one_node_group, all_nodes, group_shift)
        )

    def _render_service_row_lines(self, all_nodes: tuple[diagram_model.DiagramNode, ...], /) -> tuple[str, ...]:
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
