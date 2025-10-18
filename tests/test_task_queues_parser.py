import typing

from hypothesis import given  # type: ignore[import-untyped]
from hypothesis import strategies as st  # type: ignore[import-untyped]

from fastarch.features.task_queues.parser import find_task_queue_features


TASK_QUEUES: typing.Final = ("celery", "taskiq", "arq", "rq", "dramatiq", "huey")
BROKERS: typing.Final = ("redis", "rabbitmq", "postgresql")
_IMPORT_TEMPLATES: typing.Final = ("import {}\n", "from {} import Something\n", "from {}.worker import Worker\n")


_TASK_PATTERNS: typing.Final = {
    "celery": "from celery import Celery\napp = Celery()\n@app.task\ndef my_task():\n    pass\n",
    "taskiq": "from taskiq import TaskiqScheduler\n@broker.task\ndef my_task():\n    pass\n",
    "arq": "from arq import create_pool\n@arq.task\ndef my_task():\n    pass\n",
    "rq": "from rq import Queue\n@job\ndef my_task():\n    pass\n",
    "dramatiq": "import dramatiq\n@dramatiq.actor\ndef my_task():\n    pass\n",
    "huey": "from huey import RedisHuey\n@huey.task()\ndef my_task():\n    pass\n",
}
_WORKER_COMMANDS: typing.Final = {
    "celery": "celery worker",
    "taskiq": "taskiq worker",
    "arq": "arq worker",
    "rq": "rq worker",
    "dramatiq": "dramatiq worker",
    "huey": "huey worker",
}


@given(st.sampled_from(TASK_QUEUES))
def test_task_queue_detects_imports(queue: str) -> None:
    for template in _IMPORT_TEMPLATES:
        src = template.format(queue)
        features = find_task_queue_features(src)
        assert queue in features.queues_used


@given(st.sampled_from(TASK_QUEUES))
def test_task_queue_detects_tasks_and_workers(queue: str) -> None:
    task_features = find_task_queue_features(_TASK_PATTERNS[queue])
    assert queue in task_features.queues_used
    assert task_features.has_tasks

    worker_src = f"import {queue}\n{_WORKER_COMMANDS[queue]}\n"
    worker_features = find_task_queue_features(worker_src)
    assert queue in worker_features.queues_used
    assert worker_features.has_workers


@given(st.sampled_from(BROKERS))
def test_task_queue_detects_brokers(broker: str) -> None:
    broker_patterns = {
        "redis": "import celery\nimport redis\nredis://localhost:6379\nRedisSettings(host='localhost')\n",
        "rabbitmq": "import celery\nimport pika\namqp://localhost:5672\nRabbitMQBroker()\n",
        "postgresql": "import celery\nimport psycopg2\npostgres://localhost:5432\nPostgreSQLBroker()\n",
    }

    src = broker_patterns[broker]
    features = find_task_queue_features(src)
    assert broker in features.brokers_detected


@given(
    st.lists(
        st.sampled_from(TASK_QUEUES),
        min_size=2,
        max_size=6,
        unique=True,
    ),
)
def test_task_queue_detects_multiple_queues(queues: list[str]) -> None:
    src = "\n".join(f"import {queue}" for queue in queues)
    features = find_task_queue_features(src)

    for queue in queues:
        assert queue in features.queues_used


@given(st.text())
def test_task_queue_handles_non_queue_code(src: str) -> None:
    if not any(queue in src for queue in TASK_QUEUES):
        features = find_task_queue_features(src)
        assert len(features.queues_used) == 0
        assert not features.has_tasks
        assert not features.has_workers
        assert len(features.brokers_detected) == 0
