import fastapi
from starlette.requests import Request as StarletteRequest
from starlette.responses import HTMLResponse as StarletteHtmlResponse

from fastarch import settings
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


def _build_fastapi_arch_doc_route(arch_engine: ArchitectureParserAndRenderer) -> fastapi.APIRouter:
    async def _handle_fastapi_arch_doc_route(_: StarletteRequest) -> None:
        return StarletteHtmlResponse(settings.UI_HTML_TEMPLATE.format(arch_engine.search_features_and_draw_them()))

    return _handle_fastapi_arch_doc_route


def add_architecture_doc_routes(
    fastapi_app: fastapi.FastAPI,
    route_path: str = settings.DEFAULT_PATH,
    arch_settings: SettingsForFastarch | None = None,
) -> None:
    if arch_settings is None:
        arch_settings = SettingsForFastarch(
            root_dir=settings.DEFAULT_ROOT_DIR,
            service_name=settings.DEFAULT_SERVICE_NAME,
        )
    fastapi_app.add_api_route(route_path, _build_fastapi_arch_doc_route(ArchitectureParserAndRenderer(arch_settings)))
