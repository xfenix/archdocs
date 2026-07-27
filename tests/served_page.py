import re as py_re
import typing

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastarch import settings
from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


GOOD_HTTP_CODE: typing.Final = 200
_DIAGRAM_PATTERN: typing.Final = py_re.compile(
    r"graph LR\n(?P<diagram>.*?)</pre>",
    flags=settings.TYPICAL_RE_FLAGS,
)


def render_architecture_page(arch_settings: SettingsForFastarch | None = None) -> str:
    fastapi_app: typing.Final = FastAPI()
    add_architecture_doc_routes(fastapi_app, route_path="/", arch_settings=arch_settings)
    response: typing.Final = TestClient(fastapi_app).get("/")
    assert response.status_code == GOOD_HTTP_CODE
    return response.text


def _extract_diagram_body(page_html: str) -> str:
    diagram_match: typing.Final = _DIAGRAM_PATTERN.search(page_html)
    assert diagram_match is not None
    return diagram_match.group("diagram")


def extract_diagram(page_html: str) -> str:
    return _extract_diagram_body(page_html).replace("&lt;", "<").replace("&amp;", "&")
