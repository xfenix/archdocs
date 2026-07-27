import typing

from fastarch import mermaid_syntax, settings
from fastarch.features.messaging_queue.const import MQFeatures


def render_mq_features(features_to_draw: MQFeatures) -> str:
    diagram_parts: typing.Final[list[str]] = []
    diagram_parts.extend(
        mermaid_syntax.render_edge(one_broker, "MQ", settings.SERVICE_NODE_ID)
        for one_broker in features_to_draw.broker_names
        if features_to_draw.consumers
    )
    diagram_parts.extend(
        mermaid_syntax.render_edge(settings.SERVICE_NODE_ID, "MQ", one_broker)
        for one_broker in features_to_draw.broker_names
        if features_to_draw.producers
    )
    return "\n".join(diagram_parts)
