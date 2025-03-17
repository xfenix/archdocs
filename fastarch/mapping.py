import enum
import typing
from dataclasses import dataclass

from fastarch.features.http_api import parser as httpapi_parser
from fastarch.features.http_api import renderer as httpapi_renderer
from fastarch.features.messaging_queue import parser as mq_parser
from fastarch.features.messaging_queue import renderer as mq_renderer
from fastarch.features.redis import parser as redis_parser
from fastarch.features.redis import renderer as redis_renderer
from fastarch.features.sqlalchemy import parser as sqlalchemy_parser
from fastarch.features.sqlalchemy import renderer as sqlalchemy_renderer


@typing.final
@dataclass(frozen=True, slots=True, kw_only=True)
class _FeatureFunctions:
    parse: typing.Callable[[str], typing.Any]
    render: typing.Callable[[str, typing.Any], str]


@typing.final
class AllCurrentFeatures(enum.IntEnum):
    FASTAPI_LITESTAR = 1
    FASTSTREAM = 2
    SQLALCHEMY = 3
    REDIS = 4


MAPPING_OF_PARSERS_AND_DRAWERS: typing.Final[dict[AllCurrentFeatures, _FeatureFunctions]] = {
    AllCurrentFeatures.FASTAPI_LITESTAR: _FeatureFunctions(
        parse=httpapi_parser.find_fastapi_and_litestar_features,
        render=httpapi_renderer.draw_http_api_features,
    ),
    AllCurrentFeatures.FASTSTREAM: _FeatureFunctions(
        parse=mq_parser.find_faststream_features,
        render=mq_renderer.draw_mq_features,
    ),
    AllCurrentFeatures.SQLALCHEMY: _FeatureFunctions(
        parse=sqlalchemy_parser.find_sqlalchemy_features,
        render=sqlalchemy_renderer.draw_sqlalchemy_features,
    ),
    AllCurrentFeatures.REDIS: _FeatureFunctions(
        parse=redis_parser.find_redis_features,
        render=redis_renderer.draw_redis_features,
    ),
}
