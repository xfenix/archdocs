import typing

from fastarch import mermaid_syntax
from fastarch.features.messaging_queue.const import MQFeatures


def render_mq_features(service_node_id: str, features_to_draw: MQFeatures, /) -> str:
    diagram_parts: typing.Final[list[str]] = []
    diagram_parts.extend(
        mermaid_syntax.render_edge(mermaid_syntax.render_node_id(one_broker), "MQ", service_node_id)
        for one_broker in features_to_draw.broker_names
        if features_to_draw.consumers
    )
    diagram_parts.extend(
        mermaid_syntax.render_edge(service_node_id, "MQ", mermaid_syntax.render_node_id(one_broker))
        for one_broker in features_to_draw.broker_names
        if features_to_draw.producers
    )
    return "\n".join(diagram_parts)
