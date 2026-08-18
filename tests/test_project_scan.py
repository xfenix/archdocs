import pathlib
import types
import typing

import pytest

from archdocs.main import ArchitectureParserAndRenderer
from tests import diagram_rendering, factories, generated_project


_OWN_SOURCE: typing.Final = """import redis


cache_client = redis.Redis(host="localhost")
"""
_VENDORED_SOURCE: typing.Final = """import celery
import uvicorn


app = celery.Celery(__name__)
"""
_APPLICATION_SOURCE: typing.Final = "import fastapi\n\napp = fastapi.FastAPI()\n"
_REDIS_NODE_MARK: typing.Final = 'redisdb["redis"]'
_CHART_RELATIVE_PATH: typing.Final = "deploy/mychart"
_SOURCES_RELATIVE_PATH: typing.Final = "src"
# Two charts nothing but their own values tell apart: one belongs to the project, the other is
# what the working directory or a directory too far up would hand over instead.
_CONFIGURED_SERVICE_NAME: typing.Final = factories.SettingsFactory.build().service_name
_NEIGHBOUR_CHART: typing.Final = factories.ChartBlueprintFactory.build()
_DECOY_CHART: typing.Final = factories.ChartBlueprintFactory.build()
_TEMPLATED_CHART: typing.Final = factories.ChartBlueprintFactory.build()
_RAW_INGRESS_MANIFEST: typing.Final = f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mychart
spec:
  rules:
    - host: {_TEMPLATED_CHART.ingress_host}
"""


def _write_legacy_encoded_source(project_path: pathlib.Path, /) -> None:
    (project_path / "legacy.py").write_bytes("HEADING = 'café'\n".encode("latin-1"))


def _write_dangling_symlink(project_path: pathlib.Path, /) -> None:
    (project_path / "removed.py").symlink_to(project_path / "never-existed.py")


_ALL_UNREADABLE_SOURCES: typing.Final = types.MappingProxyType(
    {
        "legacy encoding": _write_legacy_encoded_source,
        "dangling symlink": _write_dangling_symlink,
    },
)


def _build_charted_project(
    project_path: pathlib.Path,
    /,
    *,
    chart_path: pathlib.Path | None = None,
    chart_blueprint: factories.ChartBlueprint = _NEIGHBOUR_CHART,
) -> pathlib.Path:
    source_dir: typing.Final = project_path / _SOURCES_RELATIVE_PATH
    source_dir.mkdir(parents=True)
    (source_dir / generated_project.SOURCE_FILE_NAME).write_text(_APPLICATION_SOURCE)
    generated_project.write_generated_chart(
        project_path / _CHART_RELATIVE_PATH if chart_path is None else chart_path,
        chart_blueprint,
    )
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

    rendered_diagram: typing.Final = diagram_rendering.render_diagram(
        factories.SettingsFactory.build(root_dir=project_path),
    )

    assert _REDIS_NODE_MARK in rendered_diagram
    assert "celery" not in rendered_diagram
    assert "uvicorn" not in rendered_diagram


# The scanned tree is the user's whole project: one file the process cannot decode or open used
# to raise out of the thread pool and answer the route with 500 instead of the rest of the service.
@pytest.mark.parametrize("break_one_source", _ALL_UNREADABLE_SOURCES.values(), ids=_ALL_UNREADABLE_SOURCES)
def test_unreadable_source_costs_only_itself(
    tmp_path: pathlib.Path,
    break_one_source: typing.Callable[[pathlib.Path], None],
) -> None:
    (tmp_path / "cache.py").write_text(_OWN_SOURCE)
    break_one_source(tmp_path)

    rendered_diagram: typing.Final = diagram_rendering.render_diagram(
        factories.SettingsFactory.build(root_dir=tmp_path),
    )

    assert _REDIS_NODE_MARK in rendered_diagram


@pytest.mark.parametrize("sources_subpath", [".", "one"])
def test_manifests_are_found_above_the_sources(tmp_path: pathlib.Path, sources_subpath: str) -> None:
    arch_settings: typing.Final = factories.SettingsFactory.build(
        root_dir=_build_charted_project(tmp_path / sources_subpath, chart_path=tmp_path / _CHART_RELATIVE_PATH),
        kubernetes_dir=None,
    )

    rendered_diagram: typing.Final = diagram_rendering.render_diagram(arch_settings)

    assert f'{{"{arch_settings.service_name} (replicas {_NEIGHBOUR_CHART.replica_count}' in rendered_diagram
    assert f"HTTPS {_NEIGHBOUR_CHART.ingress_host}" in rendered_diagram


def test_chart_is_found_by_its_templates(tmp_path: pathlib.Path) -> None:
    templates_dir: typing.Final = tmp_path / _CHART_RELATIVE_PATH / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "ingress.yaml").write_text(_RAW_INGRESS_MANIFEST)

    rendered_diagram: typing.Final = diagram_rendering.render_diagram(
        factories.SettingsFactory.build(root_dir=tmp_path, kubernetes_dir=None),
    )

    assert f"HTTP {_TEMPLATED_CHART.ingress_host}" in rendered_diagram


# The decoy chart is what the working directory would offer a relative path.
@pytest.mark.parametrize(
    ("kubernetes_dir", "expected_part", "forbidden_part"),
    [
        (
            diagram_rendering.KUBERNETES_VARIANTS_ROOT / "loadbalancer",
            "LoadBalancer",
            _NEIGHBOUR_CHART.ingress_host,
        ),
        ("there-is-no-such-chart", f'{{"{_CONFIGURED_SERVICE_NAME}"}}', _NEIGHBOUR_CHART.ingress_host),
        (_CHART_RELATIVE_PATH, f"HTTPS {_NEIGHBOUR_CHART.ingress_host}", _DECOY_CHART.ingress_host),
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
    _build_charted_project(decoy_project_path, chart_blueprint=_DECOY_CHART)
    monkeypatch.chdir(decoy_project_path)
    rendered_diagram: typing.Final = diagram_rendering.render_diagram(
        factories.SettingsFactory.build(
            root_dir=_build_charted_project(tmp_path / "project"),
            service_name=_CONFIGURED_SERVICE_NAME,
            kubernetes_dir=kubernetes_dir,
        ),
    )

    assert expected_part in rendered_diagram
    assert forbidden_part not in rendered_diagram


# A typo in root_dir is the emptiest possible project, not an error page: the service node
# still has to appear, alone.
def test_missing_root_dir_draws_the_service_alone(tmp_path: pathlib.Path) -> None:
    arch_settings: typing.Final = factories.SettingsFactory.build(root_dir=tmp_path / "never-created")

    rendered_diagram: typing.Final = diagram_rendering.render_diagram(arch_settings)

    assert f'{{"{arch_settings.service_name}"}}' in rendered_diagram
    assert " --> " not in rendered_diagram


# Manifests are hunted through the same foreign tree as the sources: a dangling symlink next
# to the chart used to raise out of the walk and answer the route with 500 instead of the chart.
def test_unreadable_manifest_costs_only_itself(tmp_path: pathlib.Path) -> None:
    source_dir: typing.Final = _build_charted_project(tmp_path)
    chart_dir: typing.Final = tmp_path / _CHART_RELATIVE_PATH
    (chart_dir / "broken.yaml").symlink_to(chart_dir / "never-existed.yaml")
    (chart_dir.parent / generated_project.VALUES_FILE_NAME).symlink_to(chart_dir.parent / "never-existed-values.yaml")
    arch_settings: typing.Final = factories.SettingsFactory.build(root_dir=source_dir, kubernetes_dir=None)

    rendered_diagram: typing.Final = diagram_rendering.render_diagram(arch_settings)

    assert f'{{"{arch_settings.service_name} (replicas {_NEIGHBOUR_CHART.replica_count}' in rendered_diagram
    assert f"HTTPS {_NEIGHBOUR_CHART.ingress_host}" in rendered_diagram


# A mounted route keeps one engine alive, and a rescan on every request would walk the whole
# tree again: sources edited under a running process wait for a restart, see the playground.
def test_sources_are_scanned_once_per_engine(tmp_path: pathlib.Path) -> None:
    (tmp_path / "service.py").write_text(_OWN_SOURCE)
    architecture_engine: typing.Final = ArchitectureParserAndRenderer(
        local_settings=factories.SettingsFactory.build(root_dir=tmp_path),
    )
    first_diagram: typing.Final = architecture_engine.render_architecture_diagram()

    (tmp_path / "service.py").write_text(_APPLICATION_SOURCE)
    second_diagram: typing.Final = architecture_engine.render_architecture_diagram()

    assert second_diagram == first_diagram
    assert _REDIS_NODE_MARK in second_diagram
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
        chart_blueprint=_DECOY_CHART,
    )
    if repository_marker:
        (project_path / repository_marker).mkdir()
    arch_settings: typing.Final = factories.SettingsFactory.build(root_dir=source_dir, kubernetes_dir=None)

    rendered_diagram: typing.Final = diagram_rendering.render_diagram(arch_settings)

    assert f'{{"{arch_settings.service_name}"}}' in rendered_diagram
    assert _DECOY_CHART.ingress_host not in rendered_diagram
