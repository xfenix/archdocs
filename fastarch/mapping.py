import typing

from fastarch.parsers import http_api as parsers_http_api
from fastarch.renderers import http_api as renderers_http_api


MAPPING_OF_PARSERS_AND_DRAWERS: typing.Final = {
    parsers_http_api.find_fastapi_and_litestar_features: renderers_http_api.draw_http_api_features,
}
