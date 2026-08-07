import typing

import fastapi
from fastapi.testclient import TestClient as FastapiTestClient
from litestar import Litestar
from litestar.testing import TestClient as LitestarTestClient

from archdocs.integrations import fastapi as fastapi_integration
from archdocs.integrations import litestar as litestar_integration
from archdocs.main import SettingsForArchdocs


type PageRenderer = typing.Callable[[SettingsForArchdocs | None, str | None], str]

GOOD_HTTP_CODE: typing.Final = 200
CONTENT_TYPE_HTML: typing.Final = "text/html"
# A literal, not `archdocs.settings.DEFAULT_PATH`: where the default route lives is part of the
# package's promise, and an expectation read from the code under test would prove nothing.
DEFAULT_ROUTE_PATH: typing.Final = "/docs/architecture/"


def render_fastapi_page(arch_settings: SettingsForArchdocs | None, route_path: str | None, /) -> str:
    fastapi_app: typing.Final = fastapi.FastAPI()
    if route_path is None:
        fastapi_integration.add_architecture_doc_routes(fastapi_app, arch_settings=arch_settings)
    else:
        fastapi_integration.add_architecture_doc_routes(
            fastapi_app,
            route_path=route_path,
            arch_settings=arch_settings,
        )
    fastapi_response: typing.Final = FastapiTestClient(fastapi_app).get(route_path or DEFAULT_ROUTE_PATH)
    assert fastapi_response.status_code == GOOD_HTTP_CODE
    assert CONTENT_TYPE_HTML in fastapi_response.headers["content-type"]
    return fastapi_response.text


def render_litestar_page(arch_settings: SettingsForArchdocs | None, route_path: str | None, /) -> str:
    litestar_app: typing.Final = Litestar()
    if route_path is None:
        litestar_integration.add_architecture_doc_routes(litestar_app, arch_settings=arch_settings)
    else:
        litestar_integration.add_architecture_doc_routes(
            litestar_app,
            route_path=route_path,
            arch_settings=arch_settings,
        )
    litestar_response: typing.Final = LitestarTestClient(litestar_app).get(route_path or DEFAULT_ROUTE_PATH)
    assert litestar_response.status_code == GOOD_HTTP_CODE
    assert CONTENT_TYPE_HTML in litestar_response.headers["content-type"]
    return litestar_response.text


ALL_PAGE_RENDERERS: typing.Final[tuple[PageRenderer, ...]] = (render_fastapi_page, render_litestar_page)
FRAMEWORK_IDS: typing.Final = ("fastapi", "litestar")
