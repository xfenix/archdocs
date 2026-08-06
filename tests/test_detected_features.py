import pathlib
import types
import typing

import hypothesis
import pytest
from hypothesis import strategies as st

from tests import diagram_rendering
from tests.diagram_parts import EDGE_ARROW


# What a parser found is only interesting once it reaches an arrow, so every case here is one
# source file, the diagram parts it has to draw and the parts it may not.
_EVERY_METHOD_SOURCE: typing.Final = '''import fastapi

router = fastapi.APIRouter()


@router.get("/x")
@router.post("/x")
@router.put("/x")
@router.patch("/x")
@router.delete("/x")
@router.head("/x")
@router.options("/x")
@router.trace("/x")
async def handle_everything() -> None:
    """A route is traffic the service receives whatever verb it answers."""
'''
_LITESTAR_ROUTE_SOURCE: typing.Final = """from litestar import post


@post("/items")
async def create_item(data: dict) -> dict:
    return data
"""
_ROUTE_WITHOUT_FRAMEWORK_SOURCE: typing.Final = """@router.get("/x")
async def read_items() -> list[dict]:
    return []
"""
_MOCKED_TEST_SOURCE: typing.Final = """from unittest import mock

from fastapi.testclient import TestClient


@mock.patch("src.payments.fetch_payment_status")
def test_fetching(fetch_mock: mock.MagicMock) -> None: ...
"""
_ASYNC_CLIENT_SOURCE: typing.Final = """import httpx


payments_client = httpx.AsyncClient(base_url="https://payments.example.com")
"""
_SYNC_CLIENTS_SOURCE: typing.Final = """import niquests
import requests


def fetch_payment_status(payment_id: int) -> dict:
    requests.get(f"https://payments.example.com/{payment_id}", timeout=10)
    return niquests.get(f"https://payments.example.com/{payment_id}", timeout=10).json()
"""
_CELERY_SOURCE: typing.Final = '''import celery

"""In the cluster the tasks are executed by `celery worker`."""

celery_app = celery.Celery(broker="redis://localhost:6379/0")


@celery_app.task
def send_receipt(order_id: int) -> None: ...
'''
_EVERY_QUEUE_SOURCE: typing.Final = """import arq
import celery
import dramatiq
import huey
import rq
import taskiq
"""
_RABBITMQ_BROKER_SOURCE: typing.Final = """import dramatiq


dramatiq_broker = dramatiq.RabbitMQBroker(url="amqp://localhost:5672/")
"""
_POSTGRESQL_BROKER_SOURCE: typing.Final = """import huey


huey_broker = PostgreSQLBroker("postgres://localhost:5432/tasks")
"""
_REDIS_CACHE_SOURCE: typing.Final = """import redis
import redis.asyncio


RETRY_POLICY = redis.Retry(ExponentialBackoff(), 3)
cache_client = redis.asyncio.Redis(host="cache.internal", retry=RETRY_POLICY)
"""
_REDIS_CLUSTER_SOURCE: typing.Final = """from redis.cluster import RedisCluster


cluster_client = RedisCluster(startup_nodes=[])
"""
_REDIS_SENTINEL_SOURCE: typing.Final = """from redis.sentinel import Sentinel


sentinel_client = Sentinel([("sentinel-one", 26379)])
"""
_ASYNC_REDIS_CLUSTER_SOURCE: typing.Final = """from redis.asyncio import RedisCluster


cluster_client = RedisCluster(startup_nodes=[])
"""
_ASYNC_REDIS_SENTINEL_SOURCE: typing.Final = """from redis.asyncio.sentinel import Sentinel


sentinel_client = Sentinel([("sentinel-one", 26379)])
"""
_REDIS_IMPORT_ONLY_SOURCE: typing.Final = """import redis


CACHE_HOST = "cache.internal"
"""
_ASYNC_DATABASE_SOURCE: typing.Final = """from sqlalchemy.ext.asyncio import create_async_engine


async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@pg-primary:5432/orders?target_session_attrs=read-write",
)
"""
_REPLICA_DATABASE_SOURCE: typing.Final = """from sqlalchemy import create_engine


replica_engine = create_engine(
    'postgresql+psycopg://user:password@pg-replica-one:5432,pg-replica-two:5432/orders',
    pool_size=10,
)
"""
_DOUBLE_QUOTED_REPLICA_SOURCE: typing.Final = """from sqlalchemy import create_engine


replica_engine = create_engine(
    "postgresql+psycopg://user:password@pg-replica-one:5432,pg-replica-two:5432/orders",
    pool_size=10,
)
"""
_LINES_BETWEEN_ENGINE_AND_POOL: typing.Final = 40
_POOL_FAR_FROM_THE_ENGINE_SOURCE: typing.Final = (
    "from sqlalchemy import create_engine\n\n\n"
    "replica_engine = create_engine('postgresql+psycopg://pg-replica-one:5432,pg-replica-two:5432/orders')\n"
    + "# padding that keeps the unrelated pool far away from the engine call\n" * _LINES_BETWEEN_ENGINE_AND_POOL
    + "adapter_settings = {'pool_maxsize': 10}\n"
)
_DATABASE_URL_BEHIND_A_CONSTANT_SOURCE: typing.Final = """from sqlalchemy import create_engine

from src.config import DATABASE_URL


engine = create_engine(DATABASE_URL)
"""
_CONSUMER_SOURCE: typing.Final = """from faststream import FastStream
from faststream.rabbit import RabbitBroker


rabbit_broker = RabbitBroker("amqp://user:password@localhost:5672/")
faststream_app = FastStream(rabbit_broker)


@rabbit_broker.subscriber("commands")
async def handle_command(command: dict) -> None: ...
"""
_PUBLISHER_DECORATOR_SOURCE: typing.Final = """from faststream.rabbit import RabbitBroker


rabbit_broker = RabbitBroker("amqp://localhost:5672/")


@rabbit_broker.publisher("events")
async def publish_event(event: dict) -> dict:
    return event
"""
_PUBLISH_CALL_SOURCE: typing.Final = """from faststream.rabbit import RabbitBroker


rabbit_broker = RabbitBroker("amqp://localhost:5672/")


async def publish_event(event: dict) -> None:
    await rabbit_broker.publish(event, queue="events")
"""
_TOPIC_BEHIND_A_CONSTANT_SOURCE: typing.Final = """from faststream.rabbit import RabbitBroker


COMMANDS_QUEUE = "commands"
rabbit_broker = RabbitBroker("amqp://localhost:5672/")


@rabbit_broker.subscriber(COMMANDS_QUEUE)
async def handle_command(command: dict) -> None: ...
"""
_BROKER_WITHOUT_A_FLOW_SOURCE: typing.Final = """from faststream.kafka import KafkaBroker


kafka_broker = KafkaBroker("localhost:9092")
"""
_GRANIAN_SOURCE: typing.Final = """import granian
from granian.constants import HTTPModes, Interfaces


granian.Granian(
    "src.main:app",
    port=8000,
    workers=4,
    interface=Interfaces.ASGI,
    http=HTTPModes.http2,
    ssl_cert="/etc/tls/tls.crt",
).serve()
"""
_GUNICORN_CONFIG_SOURCE: typing.Final = """bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn_worker.UvicornWorker"
"""
_CARRIER_LIBRARIES_SOURCE: typing.Final = """import gevent
import tornado.httpclient
from werkzeug.datastructures import Headers

import fastapi


app = fastapi.FastAPI()
"""
_THREAD_POOL_SOURCE: typing.Final = """from concurrent.futures import ThreadPoolExecutor

import uvicorn


executor = ThreadPoolExecutor(max_workers=10)
transport = 8080
uvicorn.run("src.main:app")
"""
_ASYNC_DATABASE_EDGE: typing.Final = (
    'app_svc --> |"async, postgresql+asyncpg://***@pg-primary:5432/orders'
    '?target_session_attrs=read-write"| postgresql_asyncpgdb'
)
_REPLICA_DATABASE_EDGE: typing.Final = (
    'app_svc --> |"postgresql+psycopg://***@pg-replica-one:5432,pg-replica-two:5432/orders"| postgresql_psycopgdb0'
)
_PLAIN_REDIS_NODE_MARK: typing.Final = "redisdb["
_CREDENTIALS_MARK: typing.Final = "user:password"
_ALL_FEATURE_CASES: typing.Final = types.MappingProxyType(
    {
        "every served method": (
            _EVERY_METHOD_SOURCE,
            ('external_client --> |"REST (delete, get, head, options, patch, post, put, trace)"| app_svc',),
            (),
        ),
        "litestar route": (
            _LITESTAR_ROUTE_SOURCE,
            ('external_client --> |"REST (post)"| app_svc',),
            (),
        ),
        "route without a framework": (_ROUTE_WITHOUT_FRAMEWORK_SOURCE, (), ("REST",)),
        "mocked test file is not an api": (_MOCKED_TEST_SOURCE, (), ("REST",)),
        "async http client": (
            _ASYNC_CLIENT_SOURCE,
            ('app_svc --> |"HTTP (async, httpx)"| External_API', 'External_API["External API"]'),
            (),
        ),
        "sync http clients": (
            _SYNC_CLIENTS_SOURCE,
            ('app_svc --> |"HTTP (niquests, requests)"| External_API',),
            ("async",),
        ),
        "task queue with a worker": (
            _CELERY_SOURCE,
            ('app_svc --> |"Tasks (celery, workers, redis)"| TaskQueue_Worker', 'TaskQueue_Worker["Task workers"]'),
            (),
        ),
        "every task queue": (
            _EVERY_QUEUE_SOURCE,
            ('app_svc --> |"Tasks (arq, celery, dramatiq, huey, rq, taskiq)"| TaskQueue_Worker',),
            (),
        ),
        "rabbitmq backed queue": (_RABBITMQ_BROKER_SOURCE, ('"Tasks (dramatiq, rabbitmq)"',), ()),
        "postgresql backed queue": (_POSTGRESQL_BROKER_SOURCE, ('"Tasks (huey, postgresql)"',), ('db["',)),
        "redis cache": (
            _REDIS_CACHE_SOURCE,
            ('app_svc --> |"async, retry"| redisdb', 'redisdb["redis"]'),
            (),
        ),
        "redis cluster": (
            _REDIS_CLUSTER_SOURCE,
            ('redisdb_cluster0["redis cluster #0"]', 'redisdb_cluster2["redis cluster #2"]', "app_svc --> redisdb"),
            (_PLAIN_REDIS_NODE_MARK,),
        ),
        "redis sentinel": (
            _REDIS_SENTINEL_SOURCE,
            ('redisdb_sentinel0["redis sentinel #0"]', 'redisdb_sentinel2["redis sentinel #2"]'),
            (_PLAIN_REDIS_NODE_MARK,),
        ),
        "redis cluster over asyncio": (
            _ASYNC_REDIS_CLUSTER_SOURCE,
            ('redisdb_cluster0["redis cluster #0"]', '|"async"|'),
            (_PLAIN_REDIS_NODE_MARK,),
        ),
        "redis sentinel over asyncio": (
            _ASYNC_REDIS_SENTINEL_SOURCE,
            ('redisdb_sentinel0["redis sentinel #0"]', '|"async"|'),
            (_PLAIN_REDIS_NODE_MARK,),
        ),
        "redis import alone": (_REDIS_IMPORT_ONLY_SOURCE, (), ("redisdb",)),
        "async database": (
            _ASYNC_DATABASE_SOURCE,
            ('postgresql_asyncpgdb["postgresql+asyncpg"]', _ASYNC_DATABASE_EDGE),
            (_CREDENTIALS_MARK,),
        ),
        "replicated database": (
            _REPLICA_DATABASE_SOURCE,
            (
                'postgresql_psycopgdb0["postgresql+psycopg #0"]',
                'postgresql_psycopgdb2["postgresql+psycopg #2"]',
                _REPLICA_DATABASE_EDGE,
            ),
            (_CREDENTIALS_MARK,),
        ),
        "replicated database in double quotes": (
            _DOUBLE_QUOTED_REPLICA_SOURCE,
            ('postgresql_psycopgdb0["postgresql+psycopg #0"]', 'postgresql_psycopgdb2["postgresql+psycopg #2"]'),
            (_CREDENTIALS_MARK,),
        ),
        "pool far from the engine call": (
            _POOL_FAR_FROM_THE_ENGINE_SOURCE,
            ('postgresql_psycopgdb0["postgresql+psycopg #0"]',),
            ("postgresql_psycopgdb1",),
        ),
        "database url behind a constant": (_DATABASE_URL_BEHIND_A_CONSTANT_SOURCE, (), ('db["',)),
        "consumed messages": (
            _CONSUMER_SOURCE,
            ('rabbit --> |"commands"| app_svc', 'rabbit["rabbit"]'),
            ("kafka", "nats", "user:password"),
        ),
        "messages published by a decorator": (
            _PUBLISHER_DECORATOR_SOURCE,
            ('app_svc --> |"events"| rabbit',),
            ("rabbit -->",),
        ),
        "messages published by a call": (
            _PUBLISH_CALL_SOURCE,
            ('app_svc --> |"events"| rabbit',),
            ("rabbit -->",),
        ),
        "topic behind a constant": (_TOPIC_BEHIND_A_CONSTANT_SOURCE, ("rabbit --> app_svc",), ('|"',)),
        "broker without a flow": (_BROKER_WITHOUT_A_FLOW_SOURCE, (), ("kafka",)),
        "application server properties": (
            _GRANIAN_SOURCE,
            ('external_client --> |"Served by granian, 4 workers, port 8000, TLS, HTTP/2"| app_svc',),
            (),
        ),
        "worker class naming both servers": (
            _GUNICORN_CONFIG_SOURCE,
            ('external_client --> |"Served by gunicorn, uvicorn, single worker, port 8000"| app_svc',),
            (),
        ),
        "carrier library is not a server": (_CARRIER_LIBRARIES_SOURCE, (), ("Served by",)),
        "thread pool is not a server worker": (
            _THREAD_POOL_SOURCE,
            ('external_client --> |"Served by uvicorn"| app_svc',),
            ("workers", "port 8080"),
        ),
    },
)
_ALL_SERVER_SOURCES: typing.Final = types.MappingProxyType(
    {
        "granian": "import granian\n\ngranian.Granian('src.main:app').serve()\n",
        "uvicorn": "import uvicorn\n\nuvicorn.run('src.main:app')\n",
        "gunicorn": "from gunicorn.app.base import BaseApplication\n",
        "hypercorn": "from hypercorn.asyncio import serve\n",
        "daphne": "from daphne.server import Server\n",
        "waitress": "from waitress import serve\n",
        "uwsgi": "import uwsgi\n",
        "mod_wsgi": "from mod_wsgi import server\n",
        "bjoern": "import bjoern\n",
        "meinheld": "from meinheld import server\n",
        "cheroot": "from cheroot.wsgi import Server\n",
        "tornado": "import tornado.httpserver\n",
        "gevent": "from gevent.pywsgi import WSGIServer\n",
        "eventlet": "import eventlet.wsgi\n",
        "werkzeug": "from werkzeug.serving import run_simple\n",
        "wsgiref": "from wsgiref.simple_server import make_server\n",
    },
)
_REQUIRED_SHOWCASE_MARKS: typing.Final = (
    "REST",
    "httpx",
    "aiohttp",
    "requests",
    "niquests",
    "celery",
    "taskiq",
    "arq",
    "rq",
    "dramatiq",
    "huey",
    "rabbit",
    "kafka",
    "nats",
    "redis",
    "retry",
    "sentinel",
    "cluster",
    "postgresql",
    "sqlite",
    "replicas",
    "HPA",
    "cpu",
    "RAM",
    "GPU",
    "ConfigMap_app_config",
    "Secret_app_secrets",
    "PersistentVolume",
    "granian",
    "gunicorn",
    "uvicorn",
)
_ALL_FEATURE_LITERALS: typing.Final = (
    *_ALL_SERVER_SOURCES,
    "fastapi",
    "litestar",
    "faststream",
    "redis",
    "sqlalchemy",
    "create_engine",
    "target_session_attrs",
    "postgresql",
    "mysql",
    "sqlite",
    "oracle",
    "mssql",
    "mariadb",
    "cockroachdb",
    "httpx",
    "aiohttp",
    "requests",
    "niquests",
    "celery",
    "taskiq",
    "arq",
    "rq",
    "dramatiq",
    "huey",
    "run_simple",
    "worker_class",
    "--worker-class",
)
_HYPOTHESIS_EXAMPLES: typing.Final = 30
_FIRST_PRINTABLE_CODE: typing.Final = 32
_LAST_PRINTABLE_CODE: typing.Final = 126
_LONGEST_RANDOM_SOURCE: typing.Final = 200


def _has_no_feature_literal(source_code: str, /) -> bool:
    return not any(one_literal in source_code.lower() for one_literal in _ALL_FEATURE_LITERALS)


_UNRELATED_SOURCE_STRATEGY: typing.Final = st.text(
    alphabet=st.characters(min_codepoint=_FIRST_PRINTABLE_CODE, max_codepoint=_LAST_PRINTABLE_CODE),
    max_size=_LONGEST_RANDOM_SOURCE,
).filter(_has_no_feature_literal)


@pytest.mark.parametrize(
    ("source_code", "expected_parts", "forbidden_parts"),
    _ALL_FEATURE_CASES.values(),
    ids=_ALL_FEATURE_CASES,
)
def test_source_reaches_the_diagram(
    tmp_path: pathlib.Path,
    source_code: str,
    expected_parts: tuple[str, ...],
    forbidden_parts: tuple[str, ...],
) -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_source_diagram(tmp_path, source_code)

    for one_expected_part in expected_parts:
        assert one_expected_part in rendered_diagram, one_expected_part
    for one_forbidden_part in forbidden_parts:
        assert one_forbidden_part not in rendered_diagram, one_forbidden_part


@pytest.mark.parametrize("server_name", _ALL_SERVER_SOURCES)
def test_every_server_reaches_the_diagram(tmp_path: pathlib.Path, server_name: str) -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_source_diagram(tmp_path, _ALL_SERVER_SOURCES[server_name])

    assert f'external_client --> |"Served by {server_name}"| app_svc' in rendered_diagram


@pytest.mark.parametrize("feature_mark", _REQUIRED_SHOWCASE_MARKS)
def test_showcase_shows_every_supported_feature(feature_mark: str) -> None:
    assert feature_mark in diagram_rendering.render_example_diagram(diagram_rendering.SHOWCASE_SETTINGS)


@hypothesis.settings(
    deadline=None,
    max_examples=_HYPOTHESIS_EXAMPLES,
    suppress_health_check=[hypothesis.HealthCheck.function_scoped_fixture],
)
@hypothesis.given(source_code=_UNRELATED_SOURCE_STRATEGY)
def test_unrelated_source_draws_the_service_alone(tmp_path: pathlib.Path, source_code: str) -> None:
    assert EDGE_ARROW not in diagram_rendering.render_source_diagram(tmp_path, source_code)
