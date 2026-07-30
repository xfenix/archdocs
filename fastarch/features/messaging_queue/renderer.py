import typing

from fastarch import diagram_model
from fastarch.features.messaging_queue.const import MQFeatures


_MQ_EDGE_LABEL: typing.Final = "MQ"


def _build_broker_node(one_broker: str, /) -> diagram_model.DiagramNode:
    return diagram_model.build_diagram_node(one_broker, one_broker, diagram_model.NodeGroup.messaging_and_tasks)


def render_mq_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: MQFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    all_edges: typing.Final[list[diagram_model.DiagramEdge]] = []
    all_edges.extend(
        diagram_model.DiagramEdge(
            source_node=_build_broker_node(one_broker),
            target_node=service_node,
            edge_label=_MQ_EDGE_LABEL,
        )
        for one_broker in features_to_draw.broker_names
        if features_to_draw.consumers
    )
    all_edges.extend(
        diagram_model.DiagramEdge(
            source_node=service_node,
            target_node=_build_broker_node(one_broker),
            edge_label=_MQ_EDGE_LABEL,
        )
        for one_broker in features_to_draw.broker_names
        if features_to_draw.producers
    )
    return tuple(all_edges)
