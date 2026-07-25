import re as py_re
import types
import typing

from fastarch import settings
from fastarch.features.task_queues.const import TaskQueueEnum, TaskQueueFeatures


_CELERY_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+celery\b|import\s+celery\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_TASKIQ_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+taskiq\b|import\s+taskiq\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_ARQ_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+arq\b|import\s+arq\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_RQ_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+rq\b|import\s+rq\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_DRAMATIQ_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+dramatiq\b|import\s+dramatiq\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_HUEY_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from\s+huey\b|import\s+huey\b)",
    flags=settings.TYPICAL_RE_FLAGS,
)

_TASK_DECORATOR_PATTERNS: typing.Final = py_re.compile(
    r"@(?:\w+\.)?(?:task|actor|job)\b",
    flags=settings.TYPICAL_RE_FLAGS,
)

_WORKER_PATTERNS: typing.Final = py_re.compile(
    r"\b(?:celery\s+worker|taskiq\s+worker|arq\s+worker|rq\s+worker|dramatiq\s+worker|huey\s+worker)\b",
    flags=settings.TYPICAL_RE_FLAGS,
)

_BROKER_PATTERNS: typing.Final = types.MappingProxyType(
    {
        "redis": py_re.compile(r"\b(?:redis://|RedisSettings|RedisHuey)\b", flags=settings.TYPICAL_RE_FLAGS),
        "rabbitmq": py_re.compile(r"\b(?:amqp://|rabbitmq://|RabbitMQBroker)\b", flags=settings.TYPICAL_RE_FLAGS),
        "postgresql": py_re.compile(
            r"\b(?:postgres://|postgresql://|PostgreSQLBroker)\b", flags=settings.TYPICAL_RE_FLAGS
        ),
    },
)

_QUEUE_IMPORT_PATTERNS: typing.Final = types.MappingProxyType(
    {
        TaskQueueEnum.CELERY: _CELERY_IMPORT_PATTERN,
        TaskQueueEnum.TASKIQ: _TASKIQ_IMPORT_PATTERN,
        TaskQueueEnum.ARQ: _ARQ_IMPORT_PATTERN,
        TaskQueueEnum.RQ: _RQ_IMPORT_PATTERN,
        TaskQueueEnum.DRAMATIQ: _DRAMATIQ_IMPORT_PATTERN,
        TaskQueueEnum.HUEY: _HUEY_IMPORT_PATTERN,
    },
)


def find_task_queue_features(raw_source: str) -> TaskQueueFeatures:
    queues_found: typing.Final[set[str]] = set()
    for queue_enum, pattern in _QUEUE_IMPORT_PATTERNS.items():
        if pattern.search(raw_source):
            queues_found.add(queue_enum.value)

    if not queues_found:
        return TaskQueueFeatures(
            queues_used=frozenset(),
            has_tasks=False,
            has_workers=False,
            brokers_detected=frozenset(),
        )

    # Combine all detection into single return statement
    return TaskQueueFeatures(
        queues_used=frozenset(queues_found),
        has_tasks=bool(_TASK_DECORATOR_PATTERNS.search(raw_source)),
        has_workers=bool(_WORKER_PATTERNS.search(raw_source)),
        brokers_detected=frozenset(
            one_broker_name
            for one_broker_name, broker_pattern in _BROKER_PATTERNS.items()
            if broker_pattern.search(raw_source)
        ),
    )
