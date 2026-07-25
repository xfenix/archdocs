import typing

from fastarch import settings
from fastarch.features.task_queues.const import TaskQueueFeatures


def render_task_queue_features(service_name: str, features_to_draw: TaskQueueFeatures) -> str:
    if not features_to_draw.queues_used:
        return ""

    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                ", ".join(sorted(features_to_draw.queues_used)),
                "workers" if features_to_draw.has_workers else "",
                ", ".join(sorted(features_to_draw.brokers_detected)) if features_to_draw.brokers_detected else "",
            ],
        ),
    )

    return f"{settings.SHIFT_LEFT}{{{service_name}}} --> |Tasks ({properties_on_arrow})| TaskQueue_Worker"
