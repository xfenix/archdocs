import pathlib
import types
import typing

import fastapi
from starlette.responses import HTMLResponse as StarletteHtmlResponse

from archdocs.integrations.fastapi import add_architecture_doc_routes
from archdocs.main import SettingsForArchdocs


TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
KUBERNETES_DIR: typing.Final = TESTS_ROOT / "kubernetes_fixtures" / "chart"
PLAYGROUND_EXAMPLES: typing.Final = types.MappingProxyType(
    {
        "fastapi": SettingsForArchdocs(
            root_dir=TESTS_ROOT / "fastapi",
            service_name="fastapi-example",
            kubernetes_dir=KUBERNETES_DIR,
        ),
        "litestar": SettingsForArchdocs(
            root_dir=TESTS_ROOT / "litestar",
            service_name="litestar-example",
            kubernetes_dir=KUBERNETES_DIR,
        ),
        "showcase": SettingsForArchdocs(
            root_dir=TESTS_ROOT / "showcase",
            service_name="showcase-service",
            kubernetes_dir=KUBERNETES_DIR,
        ),
    },
)
INDEX_PATH: typing.Final = "/"
_INDEX_TEMPLATE: typing.Final = (
    "<!doctype html><html><head><meta charset='utf-8'><title>archdocs playground</title></head>"
    "<body><h1>archdocs playground</h1><ul>{example_links}</ul></body></html>"
)


def render_example_path(example_name: str, /) -> str:
    return f"/{example_name}/"


async def _handle_index_route() -> StarletteHtmlResponse:
    example_links: typing.Final = "".join(
        f'<li><a href="{render_example_path(one_example_name)}">{one_example_settings.service_name}</a></li>'
        for one_example_name, one_example_settings in PLAYGROUND_EXAMPLES.items()
    )
    return StarletteHtmlResponse(_INDEX_TEMPLATE.format(example_links=example_links))


def create_playground_app() -> fastapi.FastAPI:
    playground_app: typing.Final = fastapi.FastAPI(title="archdocs playground")
    playground_app.add_api_route(INDEX_PATH, _handle_index_route, response_class=StarletteHtmlResponse)
    for one_example_name, one_example_settings in PLAYGROUND_EXAMPLES.items():
        add_architecture_doc_routes(
            playground_app,
            route_path=render_example_path(one_example_name),
            arch_settings=one_example_settings,
        )
    return playground_app


playground_app: typing.Final = create_playground_app()
