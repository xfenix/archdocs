import enum
import types
import typing
from dataclasses import dataclass

from fastarch.features import http_api, http_clients, messaging_queue, redis, sqlalchemy, task_queues


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
            parse=http_api.parser.find_fastapi_and_litestar_features,
            render=http_api.renderer.draw_http_api_features,
        ),
        AllCurrentFeatures.faststream: _FeatureFunctions(
            parse=messaging_queue.parser.find_faststream_features,
            render=messaging_queue.renderer.draw_mq_features,
        ),
        AllCurrentFeatures.sqlalchemy: _FeatureFunctions(
            parse=sqlalchemy.parser.find_sqlalchemy_features,
            render=sqlalchemy.renderer.draw_sqlalchemy_features,
        ),
        AllCurrentFeatures.redis: _FeatureFunctions(
            parse=redis.parser.find_redis_features,
            render=redis.renderer.draw_redis_features,
        ),
        AllCurrentFeatures.http_clients: _FeatureFunctions(
            parse=http_clients.parser.find_http_client_features,
            render=http_clients.renderer.draw_http_client_features,
        ),
        AllCurrentFeatures.task_queues: _FeatureFunctions(
            parse=task_queues.parser.find_task_queue_features,
            render=task_queues.renderer.draw_task_queue_features,
        ),
    },
)
