import types
import typing

from hypothesis import given  # type: ignore[import-untyped]
from hypothesis import strategies as st  # type: ignore[import-untyped]

from fastarch.features.task_queues.parser import find_task_queue_features


TASK_QUEUES: typing.Final = ("celery", "taskiq", "arq", "rq", "dramatiq", "huey")
BROKERS: typing.Final = ("redis", "rabbitmq", "postgresql")
_IMPORT_TEMPLATES: typing.Final = ("import {}\n", "from {} import Something\n", "from {}.worker import Worker\n")


_TASK_PATTERNS: typing.Final = types.MappingProxyType(
    {
        "celery": "from celery import Celery\napp = Celery()\n@app.task\ndef my_task():\n    pass\n",
        "taskiq": "from taskiq import TaskiqScheduler\n@broker.task\ndef my_task():\n    pass\n",
        "arq": "from arq import create_pool\n@arq.task\ndef my_task():\n    pass\n",
        "rq": "from rq import Queue\n@job\ndef my_task():\n    pass\n",
        "dramatiq": "import dramatiq\n@dramatiq.actor\ndef my_task():\n    pass\n",
        "huey": "from huey import RedisHuey\n@huey.task()\ndef my_task():\n    pass\n",
    }
)
_WORKER_COMMANDS: typing.Final = types.MappingProxyType(
    {
        "celery": "celery worker",
        "taskiq": "taskiq worker",
        "arq": "arq worker",
        "rq": "rq worker",
        "dramatiq": "dramatiq worker",
        "huey": "huey worker",
    }
)


@given(st.sampled_from(TASK_QUEUES))
def test_task_queue_detects_imports(queue_name: str) -> None:
    for one_template in _IMPORT_TEMPLATES:
        assert queue_name in find_task_queue_features(one_template.format(queue_name)).queues_used


@given(st.sampled_from(TASK_QUEUES))
def test_task_queue_detects_tasks_and_workers(queue_name: str) -> None:
    task_features: typing.Final = find_task_queue_features(_TASK_PATTERNS[queue_name])
    assert queue_name in task_features.queues_used
    assert task_features.has_tasks

    worker_features: typing.Final = find_task_queue_features(f"import {queue_name}\n{_WORKER_COMMANDS[queue_name]}\n")
    assert queue_name in worker_features.queues_used
    assert worker_features.has_workers


@given(st.sampled_from(BROKERS))
def test_task_queue_detects_brokers(broker_name: str) -> None:
    broker_patterns: typing.Final = {
        "redis": "import celery\nimport redis\nredis://localhost:6379\nRedisSettings(host='localhost')\n",
        "rabbitmq": "import celery\nimport pika\namqp://localhost:5672\nRabbitMQBroker()\n",
        "postgresql": "import celery\nimport psycopg2\npostgres://localhost:5432\nPostgreSQLBroker()\n",
    }
    assert broker_name in find_task_queue_features(broker_patterns[broker_name]).brokers_detected


@given(
    st.lists(
        st.sampled_from(TASK_QUEUES),
        min_size=2,
        max_size=6,
        unique=True,
    ),
)
def test_task_queue_detects_multiple_queues(queue_names: list[str]) -> None:
    detected_features: typing.Final = find_task_queue_features(
        "\n".join(f"import {one_queue}" for one_queue in queue_names)
    )
    for one_queue in queue_names:
        assert one_queue in detected_features.queues_used


@given(st.text())
def test_task_queue_handles_non_queue_code(source_code: str) -> None:
    if not any(one_queue in source_code for one_queue in TASK_QUEUES):
        features: typing.Final = find_task_queue_features(source_code)
        assert len(features.queues_used) == 0
        assert not features.has_tasks
        assert not features.has_workers
        assert len(features.brokers_detected) == 0
