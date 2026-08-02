import pathlib
import typing

import pytest

from archdocs.main import ArchitectureParserAndRenderer, SettingsForArchdocs
from tests.rendered_diagram import KUBERNETES_VARIANTS_ROOT, WITHOUT_MANIFESTS, render_diagram


_OWN_SOURCE: typing.Final = """import redis


cache_client = redis.Redis(host="localhost")
"""
_VENDORED_SOURCE: typing.Final = """import celery
import uvicorn


app = celery.Celery(__name__)
"""
_APPLICATION_SOURCE: typing.Final = "import fastapi\n\napp = fastapi.FastAPI()\n"
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


def _build_charted_project(
    project_path: pathlib.Path,
    /,
    *,
    chart_path: pathlib.Path | None = None,
    chart_values: str = _NEIGHBOUR_CHART_VALUES,
) -> pathlib.Path:
    source_dir: typing.Final = project_path / _SOURCES_RELATIVE_PATH
    source_dir.mkdir(parents=True)
    (source_dir / "main.py").write_text(_APPLICATION_SOURCE)
    chart_dir: typing.Final = project_path / _CHART_RELATIVE_PATH if chart_path is None else chart_path
    chart_dir.mkdir(parents=True)
    (chart_dir / "Chart.yaml").write_text("apiVersion: v2\nname: mychart\n")
    (chart_dir / "values.yaml").write_text(chart_values)
    return source_dir


# The last case is the mirror one: a service living in a `build` directory must not skip itself.
@pytest.mark.parametrize(
    ("project_subpath", "vendored_relative_path"),
    [
        (".", ".venv/lib/python3.12/site-packages/celery"),
        (".", "venv/celery"),
        (".", "node_modules/celery"),
        (".", "build/lib/celery"),
        ("build/dist/myservice", ".venv/celery"),
    ],
)
def test_dependencies_stay_out_of_the_diagram(
    tmp_path: pathlib.Path,
    project_subpath: str,
    vendored_relative_path: str,
) -> None:
    project_path: typing.Final = tmp_path / project_subpath
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "service.py").write_text(_OWN_SOURCE)
    vendored_dir: typing.Final = project_path / vendored_relative_path
    vendored_dir.mkdir(parents=True)
    (vendored_dir / "vendored.py").write_text(_VENDORED_SOURCE)

    rendered_diagram: typing.Final = render_diagram(
        SettingsForArchdocs(
            root_dir=project_path,
            service_name="vendor-svc",
            kubernetes_dir=WITHOUT_MANIFESTS,
        ),
    )

    assert 'redisdb["redis"]' in rendered_diagram
    assert "celery" not in rendered_diagram
    assert "uvicorn" not in rendered_diagram


@pytest.mark.parametrize("sources_subpath", [".", "one"])
def test_manifests_are_found_above_the_sources(tmp_path: pathlib.Path, sources_subpath: str) -> None:
    rendered_diagram: typing.Final = render_diagram(
        SettingsForArchdocs(
            root_dir=_build_charted_project(tmp_path / sources_subpath, chart_path=tmp_path / _CHART_RELATIVE_PATH),
            service_name="above-svc",
        ),
    )

    assert 'above_svc{"above-svc (replicas 4)"}' in rendered_diagram
    assert "HTTP neighbour.example.com" in rendered_diagram


def test_chart_is_found_by_its_templates(tmp_path: pathlib.Path) -> None:
    templates_dir: typing.Final = tmp_path / _CHART_RELATIVE_PATH / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "ingress.yaml").write_text(_RAW_INGRESS_MANIFEST)

    rendered_diagram: typing.Final = render_diagram(
        SettingsForArchdocs(root_dir=tmp_path, service_name="templates-svc"),
    )

    assert "HTTP from-templates.example.com" in rendered_diagram


# The decoy chart is what the working directory would offer a relative path.
@pytest.mark.parametrize(
    ("kubernetes_dir", "expected_part", "forbidden_part"),
    [
        (KUBERNETES_VARIANTS_ROOT / "loadbalancer", "LoadBalancer", "neighbour.example.com"),
        ("there-is-no-such-chart", 'config_svc{"config-svc"}', "neighbour.example.com"),
        (_CHART_RELATIVE_PATH, "HTTP neighbour.example.com", "decoy.example.com"),
    ],
)
def test_configured_dir_wins_over_the_search(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    kubernetes_dir: str | pathlib.Path,
    expected_part: str,
    forbidden_part: str,
) -> None:
    decoy_project_path: typing.Final = tmp_path / "elsewhere"
    _build_charted_project(decoy_project_path, chart_values=_DECOY_CHART_VALUES)
    monkeypatch.chdir(decoy_project_path)

    rendered_diagram: typing.Final = render_diagram(
        SettingsForArchdocs(
            root_dir=_build_charted_project(tmp_path / "project"),
            service_name="config-svc",
            kubernetes_dir=kubernetes_dir,
        ),
    )

    assert expected_part in rendered_diagram
    assert forbidden_part not in rendered_diagram


# A mounted route keeps one engine alive, and a rescan on every request would walk the whole
# tree again: sources edited under a running process wait for a restart, see the playground.
def test_sources_are_scanned_once_per_engine(tmp_path: pathlib.Path) -> None:
    (tmp_path / "service.py").write_text(_OWN_SOURCE)
    architecture_engine: typing.Final = ArchitectureParserAndRenderer(
        local_settings=SettingsForArchdocs(
            root_dir=tmp_path,
            service_name="cached-svc",
            kubernetes_dir=WITHOUT_MANIFESTS,
        ),
    )
    first_diagram: typing.Final = architecture_engine.render_architecture_diagram()

    (tmp_path / "service.py").write_text(_APPLICATION_SOURCE)
    second_diagram: typing.Final = architecture_engine.render_architecture_diagram()

    assert second_diagram == first_diagram
    assert 'redisdb["redis"]' in second_diagram
    assert "REST" not in second_diagram


@pytest.mark.parametrize(("project_subpath", "repository_marker"), [("project", ".git"), ("one/two/three", "")])
def test_far_away_manifests_are_ignored(
    tmp_path: pathlib.Path,
    project_subpath: str,
    repository_marker: str,
) -> None:
    project_path: typing.Final = tmp_path / project_subpath
    source_dir: typing.Final = _build_charted_project(
        project_path,
        chart_path=tmp_path / _CHART_RELATIVE_PATH,
        chart_values=_DECOY_CHART_VALUES,
    )
    if repository_marker:
        (project_path / repository_marker).mkdir()

    rendered_diagram: typing.Final = render_diagram(
        SettingsForArchdocs(root_dir=source_dir, service_name="far-svc"),
    )

    assert 'far_svc{"far-svc"}' in rendered_diagram
    assert "decoy.example.com" not in rendered_diagram
