import dataclasses
import enum
import typing


@typing.final
class TaskQueueEnum(enum.Enum):
    celery = "celery"
    taskiq = "taskiq"
    arq = "arq"
    rq = "rq"
    dramatiq = "dramatiq"
    huey = "huey"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class TaskQueueFeatures:
    queues_used: frozenset[str]
    has_tasks: bool
    has_workers: bool
    brokers_detected: frozenset[str]
