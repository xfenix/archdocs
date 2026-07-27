import pathlib
import typing

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastarch import mermaid_syntax
from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


_GOOD_HTTP_CODE: typing.Final = 200
_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_CHART_RELATIVE_PATH: typing.Final = "deploy/mychart"
_SOURCES_RELATIVE_PATH: typing.Final = "src"
_SIBLING_CHART_VALUES: typing.Final = """replicaCount: 4

ingress:
  enabled: true
  hosts:
    - host: sibling.example.com
"""
_DECOY_CHART_VALUES: typing.Final = """replicaCount: 9

ingress:
  enabled: true
  hosts:
    - host: decoy.example.com
"""


def _render_page(arch_settings: SettingsForFastarch) -> str:
    fastapi_app: typing.Final = FastAPI()
    add_architecture_doc_routes(fastapi_app, route_path="/", arch_settings=arch_settings)
    response: typing.Final = TestClient(fastapi_app).get("/")
    assert response.status_code == _GOOD_HTTP_CODE
    return response.text


def _build_project(
    project_path: pathlib.Path,
    /,
    *,
    chart_path: pathlib.Path | None = None,
    chart_values: str = _SIBLING_CHART_VALUES,
) -> pathlib.Path:
    """Lay out sources inside `project_path` and a chart next to them (or at `chart_path`), return the dir to scan."""
    source_dir: typing.Final = project_path / _SOURCES_RELATIVE_PATH
    source_dir.mkdir(parents=True)
    (source_dir / "main.py").write_text("import fastapi\n\napp = fastapi.FastAPI()\n")
    chart_dir: typing.Final = project_path / _CHART_RELATIVE_PATH if chart_path is None else chart_path
    chart_dir.mkdir(parents=True)
    (chart_dir / "Chart.yaml").write_text("apiVersion: v2\nname: mychart\n")
    (chart_dir / "values.yaml").write_text(chart_values)
    return source_dir


@pytest.mark.parametrize("sources_subpath", [".", "one", "one/two"])
def test_chart_found_next_to_sources(tmp_path: pathlib.Path, sources_subpath: str) -> None:
    expected_node: typing.Final = mermaid_syntax.render_service_node_definition("sibling-svc", ("replicas 4",)).strip()
    response_text: typing.Final = _render_page(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path / sources_subpath, chart_path=tmp_path / _CHART_RELATIVE_PATH),
            service_name="sibling-svc",
        ),
    )
    assert "HTTP sibling.example.com" in response_text
    assert expected_node in response_text


def test_explicit_dir_wins_over_lookup(tmp_path: pathlib.Path) -> None:
    response_text: typing.Final = _render_page(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path),
            service_name="explicit-svc",
            helm_chart_dir=_TESTS_ROOT / "helm_variants" / "loadbalancer",
        ),
    )
    assert "sibling.example.com" not in response_text
    assert "LoadBalancer" in response_text


def test_relative_dir_resolved_from_root_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    decoy_project_path: typing.Final = tmp_path / "elsewhere"
    _build_project(decoy_project_path, chart_values=_DECOY_CHART_VALUES)
    monkeypatch.chdir(decoy_project_path)
    response_text: typing.Final = _render_page(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path / "project"),
            service_name="relative-svc",
            helm_chart_dir=_CHART_RELATIVE_PATH,
        ),
    )
    assert "HTTP sibling.example.com" in response_text
    assert "decoy.example.com" not in response_text


@pytest.mark.parametrize(
    ("project_subpath", "root_marker_name"),
    [("project", "pyproject.toml"), ("one/two/three/four", "")],
)
def test_far_away_chart_is_never_picked(tmp_path: pathlib.Path, project_subpath: str, root_marker_name: str) -> None:
    project_path: typing.Final = tmp_path / project_subpath
    source_dir: typing.Final = _build_project(
        project_path,
        chart_path=tmp_path / _CHART_RELATIVE_PATH,
        chart_values=_DECOY_CHART_VALUES,
    )
    if root_marker_name:
        (project_path / root_marker_name).write_text("[project]\nname = 'neighbour'\n")
    response_text: typing.Final = _render_page(
        SettingsForFastarch(root_dir=source_dir, service_name="far-svc"),
    )
    assert "decoy.example.com" not in response_text
    assert mermaid_syntax.render_service_node_definition("far-svc").strip() in response_text


def test_missing_explicit_dir_is_ignored(tmp_path: pathlib.Path) -> None:
    response_text: typing.Final = _render_page(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path),
            service_name="missing-svc",
            helm_chart_dir=tmp_path / "there-is-no-such-chart",
        ),
    )
    assert mermaid_syntax.render_service_node_definition("missing-svc").strip() in response_text
    assert "sibling.example.com" not in response_text
