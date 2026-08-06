import re as py_re
import typing

import pytest

from archdocs.main import SettingsForArchdocs
from tests import diagram_parts, diagram_rendering


# Every rule here breaks the render silently: the page stays hidden until `postRenderCallback`
# that never fires.
_GROUP_OPENING_MARK: typing.Final = "subgraph "
_GROUP_CLOSING_LINE: typing.Final = "end"
_LINE_INDENT: typing.Final = " " * 4
# An edge is a bare node id on each end of the arrow and a label either absent or quoted whole.
_WELL_FORMED_EDGE_PATTERN: typing.Final = py_re.compile(r'[A-Za-z0-9_]+ --> (?:\|"[^"]+"\| )?[A-Za-z0-9_]+')
_ID_LESS_NODE_PATTERN: typing.Final = py_re.compile(r"(?m)^\s*\{")
_SERVICE_NODE_PATTERN: typing.Final = py_re.compile(r'(?m)^\s*(?P<node_id>[A-Za-z0-9_]+)\{"')


@pytest.mark.parametrize(diagram_rendering.SETTINGS_ARGUMENT, diagram_rendering.ALL_EXAMPLE_SETTINGS)
def test_every_line_is_valid_mermaid(arch_settings: SettingsForArchdocs) -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_example_diagram(arch_settings)

    all_lines: typing.Final = rendered_diagram.split("\n")
    all_content_lines: typing.Final = [one_line for one_line in all_lines if one_line.strip() != _GROUP_CLOSING_LINE]
    all_group_openings: typing.Final = [
        one_line.strip() for one_line in all_lines if one_line.strip().startswith(_GROUP_OPENING_MARK)
    ]
    all_broken_edges: typing.Final = [
        one_line
        for one_line in diagram_parts.extract_edge_lines(rendered_diagram)
        if not _WELL_FORMED_EDGE_PATTERN.fullmatch(one_line)
    ]
    assert not _ID_LESS_NODE_PATTERN.search(rendered_diagram)
    assert "<--" not in rendered_diagram
    assert all(one_line.startswith(_LINE_INDENT) for one_line in all_lines)
    assert all(one_line.count(diagram_parts.EDGE_ARROW) <= 1 for one_line in all_lines)
    assert all_broken_edges == []
    assert len(all_content_lines) == len(set(all_content_lines))
    assert len(all_group_openings) == len(set(all_group_openings))
    assert len(all_group_openings) == len(all_lines) - len(all_content_lines)


@pytest.mark.parametrize(diagram_rendering.SETTINGS_ARGUMENT, diagram_rendering.ALL_EXAMPLE_SETTINGS)
def test_nodes_are_defined_once_and_grouped(arch_settings: SettingsForArchdocs) -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_example_diagram(arch_settings)

    all_defined_ids: typing.Final = diagram_parts.collect_defined_node_ids(rendered_diagram)
    all_service_ids: typing.Final = {
        one_match.group("node_id") for one_match in _SERVICE_NODE_PATTERN.finditer(rendered_diagram)
    }
    all_drawn_ids: typing.Final = {
        one_node_id
        for one_edge_ends in diagram_parts.collect_edge_ends(rendered_diagram)
        for one_node_id in one_edge_ends
    }
    assert len(all_service_ids) == 1
    assert f'{{"{arch_settings.service_name}' in rendered_diagram
    assert len(all_defined_ids) == len(set(all_defined_ids))
    assert set(all_defined_ids) == set(diagram_parts.collect_group_of_every_node(rendered_diagram))
    assert all_drawn_ids <= set(all_defined_ids) | all_service_ids
