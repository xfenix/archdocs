import functools

import fastapi
from starlette.requests import Request as StarletteRequest
from starlette.responses import HTMLResponse as StarletteHtmlResponse

from archdocs import settings
from archdocs.integrations.common import _create_architecture_engine, _render_architecture_html
from archdocs.main import ArchitectureParserAndRenderer, SettingsForArchdocs


async def _handle_fastapi_arch_doc_route(
    _incoming_request: StarletteRequest,
    arch_engine: ArchitectureParserAndRenderer,
) -> StarletteHtmlResponse:
    return StarletteHtmlResponse(_render_architecture_html(arch_engine))


def add_architecture_doc_routes(
    fastapi_app: fastapi.FastAPI,
    *,
    route_path: str = settings.DEFAULT_PATH,
    arch_settings: SettingsForArchdocs | None = None,
) -> None:
    fastapi_app.add_api_route(
        route_path,
        functools.partial(
            _handle_fastapi_arch_doc_route,
            arch_engine=_create_architecture_engine(arch_settings),
        ),
    )
