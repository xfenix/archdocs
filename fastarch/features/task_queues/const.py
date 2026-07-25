import dataclasses
import enum
import typing


@typing.final
class TaskQueueEnum(enum.Enum):
    CELERY = "celery"
    TASKIQ = "taskiq"
    ARQ = "arq"
    RQ = "rq"
    DRAMATIQ = "dramatiq"
    HUEY = "huey"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class TaskQueueFeatures:
    queues_used: frozenset[str]
    has_tasks: bool
    has_workers: bool
    brokers_detected: frozenset[str]
