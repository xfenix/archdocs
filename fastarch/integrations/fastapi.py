from experimental.fastarch.integrations.fastapi import FastAPI
from starlette.requests import Request as StarletteRequest
from starlette.responses import HTMLResponse as StarletteHtmlResponse

from fastarch import settings


async def _fastapi_architecture_handler(_: StarletteRequest) -> None:
    return StarletteHtmlResponse(settings.UI_HTML_TEMPLATE.format("just for now"))


def add_architecture_doc_routes(fastapi_app: FastAPI, route_path: str = settings.DEFAULT_PATH) -> None:
    fastapi_app.add_api_route(route_path, _fastapi_architecture_handler)
