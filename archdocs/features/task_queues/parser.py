import re as py_re
import types
import typing

from archdocs import prefilter, settings
from archdocs.features.task_queues.const import TaskQueueEnum, TaskQueueFeatures


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
            r"\b(?:postgres://|postgresql://|PostgreSQLBroker)\b",
            flags=settings.TYPICAL_RE_FLAGS,
        ),
    },
)
_QUEUE_IMPORT_PATTERNS: typing.Final = types.MappingProxyType(
    {
        one_queue: py_re.compile(rf"\b(?:from|import)\s+{one_queue.value}\b", flags=settings.TYPICAL_RE_FLAGS)
        for one_queue in TaskQueueEnum
    },
)
_EMPTY_FEATURES: typing.Final = TaskQueueFeatures(
    queues_used=frozenset(),
    has_tasks=False,
    has_workers=False,
    brokers_detected=frozenset(),
)


def _find_used_queues(raw_source: str, /) -> set[str]:
    lowered_source: typing.Final = raw_source.lower()
    return {
        one_queue.value
        for one_queue, one_pattern in _QUEUE_IMPORT_PATTERNS.items()
        if prefilter.contains_any_literal(lowered_source, (one_queue.value,)) and one_pattern.search(raw_source)
    }


def find_task_queue_features(raw_source: str) -> TaskQueueFeatures:
    queues_found: typing.Final = _find_used_queues(raw_source)
    if not queues_found:
        return _EMPTY_FEATURES
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
