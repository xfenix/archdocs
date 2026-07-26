import pathlib
import typing

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastarch import mermaid_syntax, settings
from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


_GOOD_HTTP_CODE: typing.Final = 200
_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_HELM_FIXTURES_ROOT: typing.Final = _TESTS_ROOT / "helm_fixtures"
_CHART_DIR: typing.Final = _HELM_FIXTURES_ROOT / "chart"
_FIXTURE_ANNOTATIONS: typing.Final = ("replicas 3", "HPA 2-10", "target CPU 70%")
_EXPECTED_MERGED_NODE: typing.Final = mermaid_syntax.render_service_node_definition(
    "merged-svc",
    _FIXTURE_ANNOTATIONS,
).strip()


def _render_page(arch_settings: SettingsForFastarch) -> str:
    fastapi_app: typing.Final = FastAPI()
    add_architecture_doc_routes(fastapi_app, route_path="/", arch_settings=arch_settings)
    response: typing.Final = TestClient(fastapi_app).get("/")
    assert response.status_code == _GOOD_HTTP_CODE
    return response.text


def test_helm_features_rendered_via_fastapi() -> None:
    response_text: typing.Final = _render_page(
        SettingsForFastarch(root_dir=_HELM_FIXTURES_ROOT, service_name="helm-svc"),
    )
    assert "HTTPS api.example.com" in response_text
    assert "replicas 3" in response_text
    assert "HPA 2-10" in response_text
    assert "target CPU 70%" in response_text
    assert settings.SERVICE_NODE_ID in response_text


def test_explicit_chart_dir_is_honoured() -> None:
    response_text: typing.Final = _render_page(
        SettingsForFastarch(
            root_dir=_TESTS_ROOT / "fastapi",
            service_name="explicit-chart-svc",
            helm_chart_dir=_CHART_DIR,
        ),
    )
    assert "HTTPS api.example.com" in response_text
    assert "explicit-chart-svc (replicas 3" in response_text


def test_helm_and_code_share_one_node() -> None:
    response_text: typing.Final = _render_page(
        SettingsForFastarch(
            root_dir=_TESTS_ROOT / "litestar",
            service_name="merged-svc",
            helm_chart_dir=_CHART_DIR,
        ),
    )
    # The helm ingress edge and the code detected edges must attach to the very same node.
    assert "HTTPS api.example.com" in response_text
    assert "redisdb" in response_text
    assert _EXPECTED_MERGED_NODE in response_text


def test_project_without_chart_renders() -> None:
    response_text: typing.Final = _render_page(
        SettingsForFastarch(root_dir=_TESTS_ROOT / "fastapi", service_name="chartless"),
    )
    assert mermaid_syntax.render_service_node_definition("chartless").strip() in response_text
    assert "api.example.com" not in response_text
