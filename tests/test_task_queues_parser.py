import typing

from hypothesis import given  # type: ignore[import-untyped]
from hypothesis import strategies as st  # type: ignore[import-untyped]

from fastarch.features.task_queues.parser import find_task_queue_features


TASK_QUEUES: typing.Final = ["celery", "taskiq", "arq", "rq", "dramatiq", "huey"]
BROKERS: typing.Final = ["redis", "rabbitmq", "postgresql"]


@given(st.sampled_from(TASK_QUEUES))
def test_find_task_queue_features_detects_imports(queue: str) -> None:
    import_variants = [
        f"import {queue}\n",
        f"from {queue} import Something\n",
        f"from {queue}.worker import Worker\n",
    ]

    for src in import_variants:
        features = find_task_queue_features(src)
        assert queue in features.queues_used


@given(st.sampled_from(TASK_QUEUES))
def test_find_task_queue_features_detects_task_decorators(queue: str) -> None:
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


@given(st.sampled_from(TASK_QUEUES))
def test_find_task_queue_features_detects_workers(queue: str) -> None:
    worker_patterns = {
        "celery": f"import {queue}\ncelery -A myapp worker --loglevel=info\n",
        "taskiq": f"import {queue}\ntaskiq worker myapp.broker\n",
        "arq": f"import {queue}\narq myapp.worker\n",
        "rq": f"import {queue}\nrq worker\n",
        "dramatiq": f"import {queue}\ndramatiq myapp.worker\n",
        "huey": f"import {queue}\nhuey_consumer.py myapp.huey\n",
    }

    src = worker_patterns[queue]
    features = find_task_queue_features(src)
    assert queue in features.queues_used
    assert features.has_workers


@given(st.sampled_from(BROKERS))
def test_find_task_queue_features_detects_brokers(broker: str) -> None:
    broker_patterns = {
        "redis": "import redis\nredis://localhost:6379\nRedisSettings(host='localhost')\n",
        "rabbitmq": "import pika\namqp://localhost:5672\nRabbitMQBroker()\n",
        "postgresql": "import psycopg2\npostgres://localhost:5432\nPostgreSQLBroker()\n",
    }

    src = broker_patterns[broker]
    features = find_task_queue_features(src)
    assert broker in features.brokers_detected


@given(st.lists(st.sampled_from(TASK_QUEUES), min_size=2, max_size=6, unique=True))
def test_find_task_queue_features_detects_multiple_queues(queues: list[str]) -> None:
    src = "\n".join(f"import {queue}" for queue in queues)
    features = find_task_queue_features(src)

    for queue in queues:
        assert queue in features.queues_used


@given(st.text())
def test_find_task_queue_features_handles_non_queue_code(src: str) -> None:
    if not any(queue in src for queue in TASK_QUEUES):
        features = find_task_queue_features(src)
        assert len(features.queues_used) == 0
        assert not features.has_tasks
        assert not features.has_workers
        assert len(features.brokers_detected) == 0


@given(st.one_of(st.just(""), st.text().filter(lambda x: not any(queue in x for queue in TASK_QUEUES))))
def test_find_task_queue_features_edge_cases(src: str) -> None:
    features = find_task_queue_features(src)
    assert len(features.queues_used) == 0
    assert not features.has_tasks
    assert not features.has_workers
    assert len(features.brokers_detected) == 0
