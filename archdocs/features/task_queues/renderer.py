import typing

from archdocs import diagram_model
from archdocs.features.task_queues.const import TaskQueueFeatures


_TASK_WORKER_NODE: typing.Final = diagram_model.build_diagram_node(
    "TaskQueue_Worker",
    "Task workers",
    diagram_model.NodeGroup.messaging_and_tasks,
)


def render_task_queue_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: TaskQueueFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if not features_to_draw.queues_used:
        return ()

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

    return (
        diagram_model.DiagramEdge(
            source_node=service_node,
            target_node=_TASK_WORKER_NODE,
            edge_label=f"Tasks ({properties_on_arrow})",
        ),
    )
