import re as py_re
import typing

import pytest

from fastarch import settings
from fastarch.main import SettingsForFastarch
from tests.rendered_diagram import (
    ALL_EXAMPLE_SETTINGS,
    EDGE_ARROW,
    collect_defined_node_ids,
    collect_edge_ends,
    collect_group_of_every_node,
    extract_edge_lines,
    render_diagram,
)


# Mermaid breaks silently: an id-less `{name}` node, an unquoted or empty edge label, a `<--`
# arrow it has no production for, two edges glued onto one line, a `subgraph` left unclosed and
# a node defined twice or drawn without being defined all hide the whole page behind an
# unfired `postRenderCallback`. The rules are read back off a rendered diagram, because syntax
# that only holds together inside the engine proves nothing about what the browser is handed.
_SETTINGS_ARGUMENT: typing.Final = "arch_settings"
_GROUP_OPENING_MARK: typing.Final = "subgraph "
_GROUP_CLOSING_LINE: typing.Final = "end"
_EDGE_END_GROUPS: typing.Final = ("source", "target")
_NODE_ID_PATTERN: typing.Final = py_re.compile(r"^[A-Za-z0-9_]+$")
_EDGE_PATTERN: typing.Final = py_re.compile(r"^(?P<source>\S+)\s+-->\s+(?:\|(?P<label>.*)\|\s+)?(?P<target>\S+)$")
_QUOTED_LABEL_PATTERN: typing.Final = py_re.compile(r'"[^"]+"')
_ID_LESS_NODE_PATTERN: typing.Final = py_re.compile(r"(?m)^\s*\{")
_SERVICE_NODE_PATTERN: typing.Final = py_re.compile(r'(?m)^\s*(?P<node_id>[A-Za-z0-9_]+)\{"')


def _is_edge_well_formed(one_edge_line: str, /) -> bool:
    edge_match: typing.Final = _EDGE_PATTERN.match(one_edge_line)
    if edge_match is None:
        return False
    if not all(_NODE_ID_PATTERN.match(edge_match.group(one_group)) for one_group in _EDGE_END_GROUPS):
        return False
    edge_label: typing.Final = edge_match.group("label")
    return edge_label is None or bool(_QUOTED_LABEL_PATTERN.fullmatch(edge_label))


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, ALL_EXAMPLE_SETTINGS)
def test_every_line_is_valid_mermaid(arch_settings: SettingsForFastarch) -> None:
    rendered_diagram: typing.Final = render_diagram(arch_settings)

    all_lines: typing.Final = rendered_diagram.split("\n")
    # Every group ends with the same `end` keyword, so only the lines that carry content are
    # held to uniqueness, and the rest of them count the groups that were closed.
    all_content_lines: typing.Final = [one_line for one_line in all_lines if one_line.strip() != _GROUP_CLOSING_LINE]
    all_group_openings: typing.Final = [
        one_line.strip() for one_line in all_lines if one_line.strip().startswith(_GROUP_OPENING_MARK)
    ]
    all_broken_edges: typing.Final = [
        one_line for one_line in extract_edge_lines(rendered_diagram) if not _is_edge_well_formed(one_line)
    ]
    assert not _ID_LESS_NODE_PATTERN.search(rendered_diagram)
    assert "<--" not in rendered_diagram
    assert all(one_line.startswith(settings.SHIFT_LEFT) for one_line in all_lines)
    assert all(one_line.count(EDGE_ARROW) <= 1 for one_line in all_lines)
    assert all_broken_edges == []
    assert len(all_content_lines) == len(set(all_content_lines))
    assert len(all_group_openings) == len(set(all_group_openings))
    assert len(all_group_openings) == len(all_lines) - len(all_content_lines)


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, ALL_EXAMPLE_SETTINGS)
def test_nodes_are_defined_once_and_grouped(arch_settings: SettingsForFastarch) -> None:
    rendered_diagram: typing.Final = render_diagram(arch_settings)

    all_defined_ids: typing.Final = collect_defined_node_ids(rendered_diagram)
    all_service_ids: typing.Final = {
        one_match.group("node_id") for one_match in _SERVICE_NODE_PATTERN.finditer(rendered_diagram)
    }
    all_drawn_ids: typing.Final = {
        one_node_id for one_edge_ends in collect_edge_ends(rendered_diagram) for one_node_id in one_edge_ends
    }
    assert len(all_service_ids) == 1
    assert f'{{"{arch_settings.service_name}' in rendered_diagram
    assert len(all_defined_ids) == len(set(all_defined_ids))
    # The service apart, a node outside a group is a loose box in the middle of the page.
    assert set(all_defined_ids) == set(collect_group_of_every_node(rendered_diagram))
    assert all_drawn_ids <= set(all_defined_ids) | all_service_ids
