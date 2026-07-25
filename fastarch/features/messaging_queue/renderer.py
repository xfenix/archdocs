import typing

from fastarch import settings
from fastarch.features.messaging_queue.const import MQFeatures


def render_mq_features(service_name: str, features_to_draw: MQFeatures) -> str:
    diagram_parts: typing.Final[list[str]] = []
    diagram_parts.extend(
        f"{settings.SHIFT_LEFT}{one_broker} --> |MQ| {{{service_name}}}"
        for one_broker in features_to_draw.broker_names
        if features_to_draw.consumers
    )
    diagram_parts.extend(
        f"{settings.SHIFT_LEFT}{{{service_name}}} --> |MQ| {one_broker}"
        for one_broker in features_to_draw.broker_names
        if features_to_draw.producers
    )
    return "\n".join(diagram_parts)
