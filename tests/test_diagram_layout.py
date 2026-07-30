import pathlib
import re as py_re
import typing

import pytest

from fastarch.main import SettingsForFastarch
from tests.served_page import collect_group_of_every_node, render_diagram


# Mermaid has no coordinates: a diagram is laid out from arrow directions and from the order
# the lines are written in, so both are held down here. The page reads top to bottom, which
# earns `Configuration` its place above the service and `Data stores` its place below, and the
# borderless `service_row` reads left to right, which puts callers left of the service and
# everything the service reaches out to on its right. That only holds while the arrows agree
# with the side they are drawn on: one `get` route drawn as an arrow from the service back to
# its own clients used to drag the whole `Inbound API` group across the page.
_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_KUBERNETES_DIR: typing.Final = _TESTS_ROOT / "kubernetes_fixtures" / "chart"
_SETTINGS_ARGUMENT: typing.Final = "arch_settings"
_INBOUND_GROUP: typing.Final = "Inbound API"
_OUTBOUND_GROUP: typing.Final = "Outbound calls"
_EDGE_ENDS_PATTERN: typing.Final = py_re.compile(r"(?m)^\s*(?P<source>\w+) -->.* (?P<target>\w+)$")
_SHOWCASE_SETTINGS: typing.Final = SettingsForFastarch(
    root_dir=_TESTS_ROOT / "showcase",
    service_name="showcase-service",
    kubernetes_dir=_KUBERNETES_DIR,
)
_ALL_DIAGRAM_SETTINGS: typing.Final = (
    _SHOWCASE_SETTINGS,
    SettingsForFastarch(root_dir=_TESTS_ROOT / "fastapi", service_name="fastapi-svc"),
    SettingsForFastarch(root_dir=_TESTS_ROOT / "litestar", service_name="litestar-svc", kubernetes_dir=_KUBERNETES_DIR),
    SettingsForFastarch(root_dir=_TESTS_ROOT / "kubernetes_fixtures", service_name="kubernetes-svc"),
)
_PLACEMENT_ORDER_OF_MARKS: typing.Final = (
    'subgraph group_configuration["Configuration"]',
    'subgraph service_row[" "]',
    "direction LR",
    'subgraph group_inbound_api["Inbound API"]',
    'showcase_service{"',
    'subgraph group_messaging_and_tasks["Messaging & tasks"]',
    'subgraph group_outbound_calls["Outbound calls"]',
    "style service_row fill:none,stroke:none",
    'subgraph group_data_stores["Data stores"]',
)


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, _ALL_DIAGRAM_SETTINGS)
def test_arrows_agree_with_their_side(arch_settings: SettingsForFastarch) -> None:
    rendered_diagram: typing.Final = render_diagram(arch_settings)
    group_of_node: typing.Final = collect_group_of_every_node(rendered_diagram)
    all_edge_ends: typing.Final = tuple(_EDGE_ENDS_PATTERN.finditer(rendered_diagram))
    assert {
        one_match.group("target")
        for one_match in all_edge_ends
        if group_of_node.get(one_match.group("target")) == _INBOUND_GROUP
    } == set()
    assert {
        one_match.group("source")
        for one_match in all_edge_ends
        if group_of_node.get(one_match.group("source")) == _OUTBOUND_GROUP
    } == set()


def test_groups_sit_around_the_service() -> None:
    all_lines: typing.Final = [one_line.strip() for one_line in render_diagram(_SHOWCASE_SETTINGS).split("\n")]
    all_positions: typing.Final = [
        next(line_index for line_index, one_line in enumerate(all_lines) if one_line.startswith(one_mark))
        for one_mark in _PLACEMENT_ORDER_OF_MARKS
    ]
    assert all_positions == sorted(all_positions)
