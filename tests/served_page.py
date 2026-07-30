import re as py_re
import typing

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastarch import diagram_model, mermaid_syntax, settings
from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


GOOD_HTTP_CODE: typing.Final = 200
_DIAGRAM_PATTERN: typing.Final = py_re.compile(
    r"graph TB\n(?P<diagram>.*?)</pre>",
    flags=settings.TYPICAL_RE_FLAGS,
)
_GROUP_BLOCK_PATTERN: typing.Final = py_re.compile(
    r'subgraph group_\w+\["(?P<group_title>[^"]+)"\]\n(?P<group_body>.*?)\n\s*end',
    flags=py_re.DOTALL,
)
_DEFINED_NODE_PATTERN: typing.Final = py_re.compile(r'(?m)^\s*(?P<node_id>[A-Za-z0-9_]+)\["')


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


def render_diagram(arch_settings: SettingsForFastarch) -> str:
    return extract_diagram(render_architecture_page(arch_settings))


def render_service_node_id(service_name: str) -> str:
    return diagram_model.build_service_node(service_name).defined_node_id


def render_service_node_definition(service_name: str, node_annotations: typing.Iterable[str] = ()) -> str:
    return mermaid_syntax.render_node_definition(diagram_model.build_service_node(service_name, node_annotations))


def collect_group_of_every_node(rendered_diagram: str, /) -> dict[str, str]:
    return {
        one_node_match.group("node_id"): one_group_match.group("group_title")
        for one_group_match in _GROUP_BLOCK_PATTERN.finditer(rendered_diagram)
        for one_node_match in _DEFINED_NODE_PATTERN.finditer(one_group_match.group("group_body"))
    }
