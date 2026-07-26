import dataclasses
import enum
import types
import typing

from fastarch.features.helm import parser as helm_parser
from fastarch.features.helm import renderer as helm_renderer
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
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class _FeatureFunctions:
    parse_source: typing.Callable[[str], typing.Any]
    render_diagram: typing.Callable[[typing.Any], str]


@typing.final
class AllCurrentFeatures(enum.Enum):
    fastapi_litestar = 1
    faststream = 2
    sqlalchemy = 3
    redis_cache = 4
    http_clients = 5
    task_queues = 6


MAPPING_OF_PARSERS_AND_RENDERERS: typing.Final = types.MappingProxyType(
    {
        AllCurrentFeatures.fastapi_litestar: _FeatureFunctions(
            parse_source=httpapi_parser.find_fastapi_and_litestar_features,
            render_diagram=httpapi_renderer.render_http_api_features,
        ),
        AllCurrentFeatures.faststream: _FeatureFunctions(
            parse_source=mq_parser.find_faststream_features,
            render_diagram=mq_renderer.render_mq_features,
        ),
        AllCurrentFeatures.sqlalchemy: _FeatureFunctions(
            parse_source=sqlalchemy_parser.find_sqlalchemy_features,
            render_diagram=sqlalchemy_renderer.render_sqlalchemy_features,
        ),
        AllCurrentFeatures.redis_cache: _FeatureFunctions(
            parse_source=redis_parser.find_redis_features,
            render_diagram=redis_renderer.render_redis_features,
        ),
        AllCurrentFeatures.http_clients: _FeatureFunctions(
            parse_source=http_clients_parser.find_http_client_features,
            render_diagram=http_clients_renderer.render_http_client_features,
        ),
        AllCurrentFeatures.task_queues: _FeatureFunctions(
            parse_source=task_queues_parser.find_task_queue_features,
            render_diagram=task_queues_renderer.render_task_queue_features,
        ),
    },
)


# Manifest features are chart wide instead of file wide, so they live in their own registry.
# Running them through the per file loop would both duplicate their output for every source
# file and let the python parsers match chart values, for example a `redis://` broker url or
# a quoted `postgresql` dsn inside `values.yaml`, drawing edges that do not exist in the code.
@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class _ManifestFeatureFunctions:
    parse_manifests: typing.Callable[[str], typing.Any]
    render_diagram: typing.Callable[[typing.Any], str]
    render_node_annotations: typing.Callable[[typing.Any], tuple[str, ...]]


@typing.final
class AllCurrentManifestFeatures(enum.Enum):
    helm_chart = 1


MAPPING_OF_MANIFEST_PARSERS_AND_RENDERERS: typing.Final = types.MappingProxyType(
    {
        AllCurrentManifestFeatures.helm_chart: _ManifestFeatureFunctions(
            parse_manifests=helm_parser.find_helm_features,
            render_diagram=helm_renderer.render_helm_features,
            render_node_annotations=helm_renderer.render_helm_node_annotations,
        ),
    },
)
