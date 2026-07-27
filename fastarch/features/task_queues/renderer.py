import typing

from fastarch import mermaid_syntax
from fastarch.features.task_queues.const import TaskQueueFeatures


def render_task_queue_features(service_node_id: str, features_to_draw: TaskQueueFeatures, /) -> str:
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

    return mermaid_syntax.render_edge(service_node_id, f"Tasks ({properties_on_arrow})", "TaskQueue_Worker")
