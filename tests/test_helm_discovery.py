import pathlib
import typing

from fastarch.main import _find_helm_chart_dir, _read_helm_chart_source


_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_HELM_FIXTURES_ROOT: typing.Final = _TESTS_ROOT / "helm_fixtures"
_CHART_DIR: typing.Final = _HELM_FIXTURES_ROOT / "chart"


def test_chart_found_by_nested_lookup() -> None:
    assert _find_helm_chart_dir(_HELM_FIXTURES_ROOT, None) == _CHART_DIR


def test_tree_without_chart_is_empty() -> None:
    assert _find_helm_chart_dir(_TESTS_ROOT / "fastapi", None) is None


def test_explicit_chart_dir_wins() -> None:
    assert _find_helm_chart_dir(_TESTS_ROOT / "fastapi", _CHART_DIR) == _CHART_DIR


def test_explicit_missing_dir_is_empty() -> None:
    assert _find_helm_chart_dir(_HELM_FIXTURES_ROOT, _TESTS_ROOT / "there-is-no-such-chart") is None


def test_chart_found_from_sibling_dir(tmp_path: pathlib.Path) -> None:
    chart_dir: typing.Final = tmp_path / "deploy" / "mychart"
    chart_dir.mkdir(parents=True)
    (chart_dir / "Chart.yaml").write_text("apiVersion: v2\nname: mychart\n")
    (tmp_path / "src").mkdir()
    assert _find_helm_chart_dir(tmp_path / "src", None) == chart_dir


def test_chart_source_has_every_manifest() -> None:
    chart_source: typing.Final = _read_helm_chart_source(_CHART_DIR)
    assert "replicaCount" in chart_source
    assert "kind: Ingress" in chart_source
    assert "kind: HorizontalPodAutoscaler" in chart_source
    assert chart_source.endswith("\n")


def test_chart_source_is_stable(tmp_path: pathlib.Path) -> None:
    assert _read_helm_chart_source(_CHART_DIR) == _read_helm_chart_source(_CHART_DIR)
    assert _read_helm_chart_source(tmp_path) == ""
