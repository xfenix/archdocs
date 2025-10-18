import enum
import types
import typing
from dataclasses import dataclass

from fastarch.features.http_api import parser as httpapi_parser
from fastarch.features.http_api import renderer as httpapi_renderer
from fastarch.features.http_clients import parser as http_clients_parser
from fastarch.features.http_clients import renderer as http_clients_renderer
from fastarch.features.messaging_queue import parser as mq_parser
from fastarch.features.messaging_queue import renderer as mq_renderer
from fastarch.features.redis import parser as redis_parser
from fastarch.features.redis import renderer as redis_renderer
from fastarch.features.sqlalchemy import parser as sqlalchemy_parser
from fastarch.features.sqlalchemy import renderer as sqlalchemy_renderer
from fastarch.features.task_queues import parser as task_queues_parser
from fastarch.features.task_queues import renderer as task_queues_renderer


@typing.final
@dataclass(frozen=True, slots=True, kw_only=True)
class _FeatureFunctions:
    parse: typing.Callable[[str], typing.Any]
    render: typing.Callable[[str, typing.Any], str]


@typing.final
class AllCurrentFeatures(enum.Enum):
    fastapi_litestar = 1
    faststream = 2
    sqlalchemy = 3
    redis = 4
    http_clients = 5
    task_queues = 6


MAPPING_OF_PARSERS_AND_RENDERERS: typing.Final = types.MappingProxyType(
    {
        AllCurrentFeatures.fastapi_litestar: _FeatureFunctions(
            parse=httpapi_parser.find_fastapi_and_litestar_features,
            render=httpapi_renderer.draw_http_api_features,
        ),
        AllCurrentFeatures.faststream: _FeatureFunctions(
            parse=mq_parser.find_faststream_features,
            render=mq_renderer.draw_mq_features,
        ),
        AllCurrentFeatures.sqlalchemy: _FeatureFunctions(
            parse=sqlalchemy_parser.find_sqlalchemy_features,
            render=sqlalchemy_renderer.draw_sqlalchemy_features,
        ),
        AllCurrentFeatures.redis: _FeatureFunctions(
            parse=redis_parser.find_redis_features,
            render=redis_renderer.draw_redis_features,
        ),
        AllCurrentFeatures.http_clients: _FeatureFunctions(
            parse=http_clients_parser.find_http_client_features,
            render=http_clients_renderer.draw_http_client_features,
        ),
        AllCurrentFeatures.task_queues: _FeatureFunctions(
            parse=task_queues_parser.find_task_queue_features,
            render=task_queues_renderer.draw_task_queue_features,
        ),
    },
)
