import dataclasses
import enum
import pathlib
import types
import typing

from fastarch import diagram_model
from fastarch.features.app_servers import parser as app_servers_parser
from fastarch.features.app_servers import renderer as app_servers_renderer
from fastarch.features.http_api import parser as httpapi_parser
from fastarch.features.http_api import renderer as httpapi_renderer
from fastarch.features.http_clients import parser as http_clients_parser
from fastarch.features.http_clients import renderer as http_clients_renderer
from fastarch.features.kubernetes import discovery as kubernetes_discovery
from fastarch.features.kubernetes import parser as kubernetes_parser
from fastarch.features.kubernetes import renderer as kubernetes_renderer
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
    render_diagram: typing.Callable[[diagram_model.DiagramNode, typing.Any], tuple[diagram_model.DiagramEdge, ...]]


@typing.final
class AllCurrentFeatures(enum.Enum):
    fastapi_litestar = 1
    faststream = 2
    sqlalchemy = 3
    redis_cache = 4
    http_clients = 5
    task_queues = 6
    app_servers = 7


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
        AllCurrentFeatures.app_servers: _FeatureFunctions(
            parse_source=app_servers_parser.find_application_server_features,
            render_diagram=app_servers_renderer.render_application_server_features,
        ),
    },
)


@typing.final
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ManifestFeatureFunctions:
    read_source: typing.Callable[[pathlib.Path, str | pathlib.Path | None], str]
    parse_manifests: typing.Callable[[str], typing.Any]
    render_diagram: typing.Callable[[diagram_model.DiagramNode, typing.Any], tuple[diagram_model.DiagramEdge, ...]]
    render_node_annotations: typing.Callable[[typing.Any], tuple[str, ...]]


@typing.final
class AllCurrentManifestFeatures(enum.Enum):
    kubernetes = 1


MAPPING_OF_MANIFEST_PARSERS_AND_RENDERERS: typing.Final = types.MappingProxyType(
    {
        AllCurrentManifestFeatures.kubernetes: ManifestFeatureFunctions(
            read_source=kubernetes_discovery.read_kubernetes_manifests,
            parse_manifests=kubernetes_parser.find_kubernetes_features,
            render_diagram=kubernetes_renderer.render_kubernetes_features,
            render_node_annotations=kubernetes_renderer.render_kubernetes_node_annotations,
        ),
    },
)
