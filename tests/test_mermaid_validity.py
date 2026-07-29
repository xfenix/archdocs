import pathlib
import re as py_re
import typing

import pytest

from fastarch import mermaid_syntax, settings
from fastarch.main import SettingsForFastarch
from tests.served_page import extract_diagram, render_architecture_page


# These invariants encode the mermaid syntax rules the renderers used to break silently:
# an id-less `{name}` node, an unquoted or empty edge label, a `<--` arrow that mermaid
# has no production for, and two edges glued onto a single physical line. They are read
# back off the served page, because a diagram that only holds together inside the engine
# proves nothing about what the browser is handed.
_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_SETTINGS_ARGUMENT: typing.Final = "arch_settings"
_NODE_ID_PATTERN: typing.Final = py_re.compile(r"^[A-Za-z0-9_]+$")
_EDGE_PATTERN: typing.Final = py_re.compile(r"^(?P<source>\S+)\s+-->\s+(?:\|(?P<label>.*)\|\s+)?(?P<target>\S+)$")
_ID_LESS_NODE_PATTERN: typing.Final = py_re.compile(r"(?m)^\s*\{")
_ALL_DIAGRAM_SETTINGS: typing.Final = (
    SettingsForFastarch(root_dir=_TESTS_ROOT / "fastapi", service_name="fastapi-svc"),
    SettingsForFastarch(root_dir=_TESTS_ROOT / "litestar", service_name="litestar-svc"),
    SettingsForFastarch(root_dir=_TESTS_ROOT / "kubernetes_fixtures", service_name="kubernetes-svc"),
    SettingsForFastarch(
        root_dir=_TESTS_ROOT / "litestar",
        service_name="merged-svc",
        kubernetes_dir=_TESTS_ROOT / "kubernetes_fixtures" / "chart",
    ),
)


def _render(arch_settings: SettingsForFastarch) -> str:
    return extract_diagram(render_architecture_page(arch_settings))


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, _ALL_DIAGRAM_SETTINGS)
def test_no_id_less_node_or_reverse_arrow(arch_settings: SettingsForFastarch) -> None:
    rendered_diagram: typing.Final = _render(arch_settings)
    assert "| {" not in rendered_diagram
    assert not _ID_LESS_NODE_PATTERN.search(rendered_diagram)
    assert "<--" not in rendered_diagram


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, _ALL_DIAGRAM_SETTINGS)
def test_lines_are_indented_and_unique(arch_settings: SettingsForFastarch) -> None:
    all_lines: typing.Final = _render(arch_settings).split("\n")
    assert all(one_line.startswith(settings.SHIFT_LEFT) for one_line in all_lines)
    assert all(one_line.count(" --> ") <= 1 for one_line in all_lines)
    assert len(all_lines) == len(set(all_lines))


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, _ALL_DIAGRAM_SETTINGS)
def test_every_edge_is_well_formed(arch_settings: SettingsForFastarch) -> None:
    all_edge_lines: typing.Final = [
        one_line.strip() for one_line in _render(arch_settings).split("\n") if " --> " in one_line
    ]
    for one_edge_line in all_edge_lines:
        edge_match = _EDGE_PATTERN.match(one_edge_line)
        assert edge_match is not None, one_edge_line
        assert _NODE_ID_PATTERN.match(edge_match.group("source")), one_edge_line
        assert _NODE_ID_PATTERN.match(edge_match.group("target")), one_edge_line
        assert _is_label_valid(edge_match.group("label")), one_edge_line


def _is_label_valid(edge_label: str | None) -> bool:
    # A label is optional, but when present it has to be quoted and non empty.
    if edge_label is None:
        return True
    if not edge_label.startswith('"') or not edge_label.endswith('"'):
        return False
    return bool(edge_label.strip('"'))


def test_credentials_never_reach_diagram() -> None:
    rendered_diagram: typing.Final = _render(
        SettingsForFastarch(root_dir=_TESTS_ROOT / "litestar", service_name="litestar-svc"),
    )
    assert "user:password" not in rendered_diagram
    assert "://***@" in rendered_diagram


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, _ALL_DIAGRAM_SETTINGS)
def test_service_node_defined_exactly_once(arch_settings: SettingsForFastarch) -> None:
    service_node_id: typing.Final = mermaid_syntax.render_service_node_id(arch_settings.service_name)
    all_lines: typing.Final = _render(arch_settings).split("\n")
    node_definitions: typing.Final = [
        one_line for one_line in all_lines if one_line.strip().startswith(service_node_id) and " --> " not in one_line
    ]
    assert len(node_definitions) == 1
    assert node_definitions[0] == all_lines[0]
