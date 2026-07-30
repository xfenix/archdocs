import typing

from fastarch import diagram_model
from fastarch.features.messaging_queue.const import BrokerFlow, MQFeatures


def _build_broker_node(one_broker: str, /) -> diagram_model.DiagramNode:
    return diagram_model.build_diagram_node(one_broker, one_broker, diagram_model.NodeGroup.messaging_and_tasks)


def _render_flow_edges(
    service_node: diagram_model.DiagramNode,
    one_flow: BrokerFlow,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    broker_node: typing.Final = _build_broker_node(one_flow.broker_name)
    all_edges: typing.Final[list[diagram_model.DiagramEdge]] = []
    if one_flow.consumes:
        all_edges.append(
            diagram_model.DiagramEdge(
                source_node=broker_node,
                target_node=service_node,
                edge_label=", ".join(one_flow.consumed_topics),
            ),
        )
    if one_flow.produces:
        all_edges.append(
            diagram_model.DiagramEdge(
                source_node=service_node,
                target_node=broker_node,
                edge_label=", ".join(one_flow.produced_topics),
            ),
        )
    return tuple(all_edges)


def render_mq_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: MQFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    return tuple(
        one_edge
        for one_flow in features_to_draw.broker_flows
        for one_edge in _render_flow_edges(service_node, one_flow)
    )
