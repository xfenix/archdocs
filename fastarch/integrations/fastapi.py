import fastapi
from starlette.requests import Request as StarletteRequest
from starlette.responses import HTMLResponse as StarletteHtmlResponse

from fastarch import settings
from fastarch.main import FeaturesInSourceFinder


def _build_fastapi_arch_doc_route(finder_cls: type[FeaturesInSourceFinder]) -> fastapi.APIRouter:
    async def _handle_fastapi_arch_doc_route(_: StarletteRequest) -> None:
        return StarletteHtmlResponse(settings.UI_HTML_TEMPLATE.format(finder_cls.search_features_and_draw_them()))

    return _handle_fastapi_arch_doc_route


def add_architecture_doc_routes(
    fastapi_app: fastapi.FastAPI,
    finder_cls: type[FeaturesInSourceFinder],
    route_path: str = settings.DEFAULT_PATH,
) -> None:
    fastapi_app.add_api_route(route_path, _build_fastapi_arch_doc_route(finder_cls))
