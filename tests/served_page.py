import typing

import fastapi
from fastapi.testclient import TestClient as FastapiTestClient
from litestar import Litestar
from litestar.testing import TestClient as LitestarTestClient

from fastarch import settings
from fastarch.integrations import fastapi as fastapi_integration
from fastarch.integrations import litestar as litestar_integration
from fastarch.main import SettingsForFastarch


type PageRenderer = typing.Callable[[SettingsForFastarch | None, str | None], str]

GOOD_HTTP_CODE: typing.Final = 200
CONTENT_TYPE_HTML: typing.Final = "text/html"


def render_fastapi_page(arch_settings: SettingsForFastarch | None, route_path: str | None, /) -> str:
    fastapi_app: typing.Final = fastapi.FastAPI()
    if route_path is None:
        fastapi_integration.add_architecture_doc_routes(fastapi_app, arch_settings=arch_settings)
    else:
        fastapi_integration.add_architecture_doc_routes(
            fastapi_app,
            route_path=route_path,
            arch_settings=arch_settings,
        )
    fastapi_response: typing.Final = FastapiTestClient(fastapi_app).get(route_path or settings.DEFAULT_PATH)
    assert fastapi_response.status_code == GOOD_HTTP_CODE
    assert CONTENT_TYPE_HTML in fastapi_response.headers["content-type"]
    return fastapi_response.text


def render_litestar_page(arch_settings: SettingsForFastarch | None, route_path: str | None, /) -> str:
    litestar_app: typing.Final = Litestar()
    if route_path is None:
        litestar_integration.add_architecture_doc_routes(litestar_app, arch_settings=arch_settings)
    else:
        litestar_integration.add_architecture_doc_routes(
            litestar_app,
            route_path=route_path,
            arch_settings=arch_settings,
        )
    litestar_response: typing.Final = LitestarTestClient(litestar_app).get(route_path or settings.DEFAULT_PATH)
    assert litestar_response.status_code == GOOD_HTTP_CODE
    assert CONTENT_TYPE_HTML in litestar_response.headers["content-type"]
    return litestar_response.text


ALL_PAGE_RENDERERS: typing.Final[tuple[PageRenderer, ...]] = (render_fastapi_page, render_litestar_page)
FRAMEWORK_IDS: typing.Final = ("fastapi", "litestar")
