import pathlib
import typing

import pytest

from fastarch.main import SettingsForFastarch
from tests.served_page import render_architecture_page, render_service_node_definition


_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_CHART_RELATIVE_PATH: typing.Final = "deploy/mychart"
_SOURCES_RELATIVE_PATH: typing.Final = "src"
_NEIGHBOUR_CHART_VALUES: typing.Final = """replicaCount: 4

ingress:
  enabled: true
  hosts:
    - host: neighbour.example.com
"""
_RAW_INGRESS_MANIFEST: typing.Final = """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mychart
spec:
  rules:
    - host: from-templates.example.com
"""
_DECOY_CHART_VALUES: typing.Final = """replicaCount: 9

ingress:
  enabled: true
  hosts:
    - host: decoy.example.com
"""


def _build_project(
    project_path: pathlib.Path,
    /,
    *,
    chart_path: pathlib.Path | None = None,
    chart_values: str = _NEIGHBOUR_CHART_VALUES,
) -> pathlib.Path:
    source_dir: typing.Final = project_path / _SOURCES_RELATIVE_PATH
    source_dir.mkdir(parents=True)
    (source_dir / "main.py").write_text("import fastapi\n\napp = fastapi.FastAPI()\n")
    chart_dir: typing.Final = project_path / _CHART_RELATIVE_PATH if chart_path is None else chart_path
    chart_dir.mkdir(parents=True)
    (chart_dir / "Chart.yaml").write_text("apiVersion: v2\nname: mychart\n")
    (chart_dir / "values.yaml").write_text(chart_values)
    return source_dir


@pytest.mark.parametrize("sources_subpath", [".", "one"])
def test_manifests_found_above_the_sources(tmp_path: pathlib.Path, sources_subpath: str) -> None:
    expected_node: typing.Final = render_service_node_definition("above-svc", ("replicas 4",))
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path / sources_subpath, chart_path=tmp_path / _CHART_RELATIVE_PATH),
            service_name="above-svc",
        ),
    )
    assert "HTTP neighbour.example.com" in response_text
    assert expected_node in response_text


def test_chart_found_by_its_templates(tmp_path: pathlib.Path) -> None:
    templates_dir: typing.Final = tmp_path / _CHART_RELATIVE_PATH / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "ingress.yaml").write_text(_RAW_INGRESS_MANIFEST)
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(root_dir=tmp_path, service_name="templates-svc"),
    )
    assert "HTTP from-templates.example.com" in response_text


def test_explicit_dir_wins_over_lookup(tmp_path: pathlib.Path) -> None:
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path),
            service_name="explicit-svc",
            kubernetes_dir=_TESTS_ROOT / "kubernetes_variants" / "loadbalancer",
        ),
    )
    assert "neighbour.example.com" not in response_text
    assert "LoadBalancer" in response_text


def test_relative_dir_resolved_from_root_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    decoy_project_path: typing.Final = tmp_path / "elsewhere"
    _build_project(decoy_project_path, chart_values=_DECOY_CHART_VALUES)
    monkeypatch.chdir(decoy_project_path)
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path / "project"),
            service_name="relative-svc",
            kubernetes_dir=_CHART_RELATIVE_PATH,
        ),
    )
    assert "HTTP neighbour.example.com" in response_text
    assert "decoy.example.com" not in response_text


def test_missing_explicit_dir_is_ignored(tmp_path: pathlib.Path) -> None:
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path),
            service_name="missing-svc",
            kubernetes_dir=tmp_path / "there-is-no-such-chart",
        ),
    )
    assert render_service_node_definition("missing-svc") in response_text
    assert "neighbour.example.com" not in response_text


# Two guards keep the lookup off a chart that belongs to somebody else: the repository the
# sources live in, and the two levels the lookup is allowed to climb.
@pytest.mark.parametrize(("project_subpath", "repository_marker"), [("project", ".git"), ("one/two/three", "")])
def test_far_away_manifests_are_ignored(
    tmp_path: pathlib.Path,
    project_subpath: str,
    repository_marker: str,
) -> None:
    project_path: typing.Final = tmp_path / project_subpath
    source_dir: typing.Final = _build_project(
        project_path,
        chart_path=tmp_path / _CHART_RELATIVE_PATH,
        chart_values=_DECOY_CHART_VALUES,
    )
    if repository_marker:
        (project_path / repository_marker).mkdir()
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(root_dir=source_dir, service_name="far-svc"),
    )
    assert "decoy.example.com" not in response_text
    assert render_service_node_definition("far-svc") in response_text
