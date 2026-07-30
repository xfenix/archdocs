import dataclasses
import enum
import re as py_re
import typing

from fastarch import settings


_UNSAFE_NODE_ID_PATTERN: typing.Final = py_re.compile(r"[^A-Za-z0-9_]+")


@typing.final
class NodeShape(enum.Enum):
    plain_node = '{defined_node_id}["{node_label}"]'
    service_node = '{defined_node_id}{{"{node_label}"}}'


# Declaration order is emission order, and mermaid lays a group out where its first line
# appears: brokers written after `Outbound calls` are dragged out of the service row and over
# the whole diagram, because half their arrows point back at the service. `diagram_layout`
# turns this order into sides of the page.
@typing.final
class NodeGroup(enum.Enum):
    inbound_api = "Inbound API"
    messaging_and_tasks = "Messaging & tasks"
    outbound_calls = "Outbound calls"
    data_stores = "Data stores"
    configuration = "Configuration"


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DiagramNode:
    defined_node_id: str
    node_label: str
    node_group: NodeGroup | None = None
    node_shape: NodeShape = NodeShape.plain_node


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DiagramEdge:
    source_node: DiagramNode
    target_node: DiagramNode
    edge_label: str = ""


def render_node_id(raw_node_name: str) -> str:
    return _UNSAFE_NODE_ID_PATTERN.sub("_", raw_node_name).strip("_")


def build_diagram_node(raw_node_name: str, node_label: str, node_group: NodeGroup, /) -> DiagramNode:
    return DiagramNode(defined_node_id=render_node_id(raw_node_name), node_label=node_label, node_group=node_group)


def build_service_node(service_name: str, node_annotations: typing.Iterable[str] = ()) -> DiagramNode:
    joined_annotations: typing.Final = ", ".join(filter(None, node_annotations))
    return DiagramNode(
        defined_node_id=render_node_id(service_name) or settings.FALLBACK_SERVICE_NODE_ID,
        node_label=f"{service_name} ({joined_annotations})" if joined_annotations else service_name,
        node_shape=NodeShape.service_node,
    )


EXTERNAL_CLIENT_NODE: typing.Final = DiagramNode(
    defined_node_id=settings.EXTERNAL_CLIENT_NODE_ID,
    node_label=settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA,
    node_group=NodeGroup.inbound_api,
)
EXTERNAL_API_NODE: typing.Final = DiagramNode(
    defined_node_id=settings.EXTERNAL_API_NODE_ID,
    node_label=settings.EXTERNAL_API_TITLE_FOR_SCHEMA,
    node_group=NodeGroup.outbound_calls,
)
