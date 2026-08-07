import dataclasses
import enum
import typing


@typing.final
class TaskQueueEnum(enum.Enum):
    celery_queue = "celery"
    taskiq_queue = "taskiq"
    arq_queue = "arq"
    rq_queue = "rq"
    dramatiq_queue = "dramatiq"
    huey_queue = "huey"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class TaskQueueFeatures:
    queues_used: frozenset[str]
    has_workers: bool
    brokers_detected: frozenset[str]
