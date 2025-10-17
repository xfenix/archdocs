import functools
import typing

import fastapi
from starlette.requests import Request as StarletteRequest
from starlette.responses import HTMLResponse as StarletteHtmlResponse

from fastarch import settings
from fastarch.integrations.common import _create_architecture_engine, _generate_architecture_html
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


async def _handle_fastapi_arch_doc_route(
    _: StarletteRequest,
    arch_engine: ArchitectureParserAndRenderer,
) -> StarletteHtmlResponse:
    return StarletteHtmlResponse(_generate_architecture_html(arch_engine))


def _build_fastapi_arch_doc_route(
    arch_engine: ArchitectureParserAndRenderer,
) -> typing.Callable[[StarletteRequest], typing.Awaitable[StarletteHtmlResponse]]:
    return functools.partial(_handle_fastapi_arch_doc_route, arch_engine=arch_engine)


def add_architecture_doc_routes(
    fastapi_app: fastapi.FastAPI,
    route_path: str = settings.DEFAULT_PATH,
    arch_settings: SettingsForFastarch | None = None,
) -> None:
    arch_engine: typing.Final = _create_architecture_engine(arch_settings)
    fastapi_app.add_api_route(route_path, _build_fastapi_arch_doc_route(arch_engine))
