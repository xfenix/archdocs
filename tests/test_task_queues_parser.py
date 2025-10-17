import typing

from hypothesis import given  # type: ignore[import-untyped]
from hypothesis import strategies as st  # type: ignore[import-untyped]

from fastarch.features.task_queues.parser import find_task_queue_features


TASK_QUEUES: typing.Final = ("celery", "taskiq", "arq", "rq", "dramatiq", "huey")
BROKERS: typing.Final = ("redis", "rabbitmq", "postgresql")
_IMPORT_TEMPLATES: typing.Final = ("import {}\n", "from {} import Something\n", "from {}.worker import Worker\n")


def _has_no_queues(text: str) -> bool:
    return not any(queue in text for queue in TASK_QUEUES)


@given(st.sampled_from(TASK_QUEUES))
def test_task_queue_detects_imports(queue: str) -> None:
    for template in _IMPORT_TEMPLATES:
        src = template.format(queue)
        features = find_task_queue_features(src)
        assert queue in features.queues_used


@given(st.sampled_from(TASK_QUEUES))
def test_task_queue_detects_task_decorators(queue: str) -> None:
    task_patterns = {
        "celery": "from celery import Celery\napp = Celery()\n@app.task\ndef my_task():\n    pass\n",
        "taskiq": "from taskiq import TaskiqScheduler\n@broker.task\ndef my_task():\n    pass\n",
        "arq": "from arq import create_pool\n@arq.task\ndef my_task():\n    pass\n",
        "rq": "from rq import Queue\n@job\ndef my_task():\n    pass\n",
        "dramatiq": "import dramatiq\n@dramatiq.actor\ndef my_task():\n    pass\n",
        "huey": "from huey import RedisHuey\n@huey.task()\ndef my_task():\n    pass\n",
    }

    src = task_patterns[queue]
    features = find_task_queue_features(src)
    assert queue in features.queues_used
    assert features.has_tasks


def _create_worker_pattern(queue: str) -> str:
    worker_commands = {
        "celery": "celery worker",
        "taskiq": "taskiq worker",
        "arq": "arq worker",
        "rq": "rq worker",
        "dramatiq": "dramatiq worker",
        "huey": "huey worker",
    }
    return f"import {queue}\n{worker_commands[queue]}\n"


@given(st.sampled_from(TASK_QUEUES))
def test_task_queue_detects_workers(queue: str) -> None:
    src = _create_worker_pattern(queue)
    features = find_task_queue_features(src)
    assert queue in features.queues_used
    assert features.has_workers


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


@given(st.lists(st.sampled_from(TASK_QUEUES), min_size=2, max_size=6, unique=True))
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


@given(st.one_of(st.just(""), st.text().filter(_has_no_queues)))
def test_task_queue_edge_cases(src: str) -> None:
    features = find_task_queue_features(src)
    assert len(features.queues_used) == 0
    assert not features.has_tasks
    assert not features.has_workers
    assert len(features.brokers_detected) == 0
