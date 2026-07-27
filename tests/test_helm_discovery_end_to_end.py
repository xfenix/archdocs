import pathlib
import typing

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastarch import mermaid_syntax
from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


_GOOD_HTTP_CODE: typing.Final = 200
_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_SIBLING_CHART_VALUES: typing.Final = """replicaCount: 4

ingress:
  enabled: true
  hosts:
    - host: sibling.example.com
"""


def _render_page(arch_settings: SettingsForFastarch) -> str:
    fastapi_app: typing.Final = FastAPI()
    add_architecture_doc_routes(fastapi_app, route_path="/", arch_settings=arch_settings)
    response: typing.Final = TestClient(fastapi_app).get("/")
    assert response.status_code == _GOOD_HTTP_CODE
    return response.text


def _build_sibling_project(tmp_path: pathlib.Path) -> pathlib.Path:
    source_dir: typing.Final = tmp_path / "src"
    source_dir.mkdir()
    (source_dir / "main.py").write_text("import fastapi\n\napp = fastapi.FastAPI()\n")
    chart_dir: typing.Final = tmp_path / "deploy" / "mychart"
    chart_dir.mkdir(parents=True)
    (chart_dir / "Chart.yaml").write_text("apiVersion: v2\nname: mychart\n")
    (chart_dir / "values.yaml").write_text(_SIBLING_CHART_VALUES)
    return source_dir


def test_chart_found_next_to_sources(tmp_path: pathlib.Path) -> None:
    expected_node: typing.Final = mermaid_syntax.render_service_node_definition("sibling-svc", ("replicas 4",)).strip()
    response_text: typing.Final = _render_page(
        SettingsForFastarch(root_dir=_build_sibling_project(tmp_path), service_name="sibling-svc"),
    )
    assert "HTTP sibling.example.com" in response_text
    assert expected_node in response_text


def test_explicit_dir_wins_over_lookup(tmp_path: pathlib.Path) -> None:
    response_text: typing.Final = _render_page(
        SettingsForFastarch(
            root_dir=_build_sibling_project(tmp_path),
            service_name="explicit-svc",
            helm_chart_dir=_TESTS_ROOT / "helm_variants" / "loadbalancer",
        ),
    )
    assert "sibling.example.com" not in response_text
    assert "LoadBalancer" in response_text


def test_missing_explicit_dir_is_ignored(tmp_path: pathlib.Path) -> None:
    response_text: typing.Final = _render_page(
        SettingsForFastarch(
            root_dir=_build_sibling_project(tmp_path),
            service_name="missing-svc",
            helm_chart_dir=tmp_path / "there-is-no-such-chart",
        ),
    )
    assert mermaid_syntax.render_service_node_definition("missing-svc").strip() in response_text
    assert "sibling.example.com" not in response_text
