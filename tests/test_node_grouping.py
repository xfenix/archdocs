import pathlib
import re as py_re
import typing

import pytest

from fastarch import diagram_model, mermaid_syntax
from fastarch.main import SettingsForFastarch
from tests.served_page import extract_diagram, render_architecture_page


# Grouping is what keeps the page from falling apart into a field of loose boxes: everything
# the service talks to sits in one of the labelled groups, and neighbours of a kind share it.
# Expectations are literal ids and titles read back off the served page, and the showcase
# example carries them because it is the one example with every supported technology at once.
# The structural half of the file guards the two ways grouping breaks a diagram silently: a
# `subgraph` left unclosed, and a node defined twice or drawn without being defined at all.
_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_KUBERNETES_DIR: typing.Final = _TESTS_ROOT / "kubernetes_fixtures" / "chart"
_SETTINGS_ARGUMENT: typing.Final = "arch_settings"
_SERVICE_NODE_ID: typing.Final = "showcase_service"
_MESSAGING_GROUP: typing.Final = "Messaging & tasks"
_DATA_STORES_GROUP: typing.Final = "Data stores"
_CONFIGURATION_GROUP: typing.Final = "Configuration"
_GROUP_OPENING_MARK: typing.Final = "subgraph "
_GROUP_CLOSING_LINE: typing.Final = "end"
_EDGE_ARROW: typing.Final = " --> "
_GROUP_BLOCK_PATTERN: typing.Final = py_re.compile(
    r'subgraph \w+\["(?P<group_title>[^"]+)"\]\n(?P<group_body>.*?)\n\s*end',
    flags=py_re.DOTALL,
)
_DEFINED_NODE_PATTERN: typing.Final = py_re.compile(r'(?m)^\s*(?P<node_id>[A-Za-z0-9_]+)\["')
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
_EXPECTED_GROUP_OF_NODE: typing.Final = (
    ("external_client", "Inbound API"),
    ("External_API", "Outbound calls"),
    ("rabbit", _MESSAGING_GROUP),
    ("kafka", _MESSAGING_GROUP),
    ("nats", _MESSAGING_GROUP),
    ("redis", _MESSAGING_GROUP),
    ("TaskQueue_Worker", _MESSAGING_GROUP),
    ("postgresql_asyncpgdb", _DATA_STORES_GROUP),
    ("postgresql_psycopgdb0", _DATA_STORES_GROUP),
    ("sqlite_aiosqlitedb", _DATA_STORES_GROUP),
    ("redisdb", _DATA_STORES_GROUP),
    ("redisdb0", _DATA_STORES_GROUP),
    ("PersistentVolume", _DATA_STORES_GROUP),
    ("ConfigMap_app_config", _CONFIGURATION_GROUP),
    ("Secret_app_secrets", _CONFIGURATION_GROUP),
)


def _render(arch_settings: SettingsForFastarch) -> str:
    return extract_diagram(render_architecture_page(arch_settings))


def _collect_group_of_every_node(rendered_diagram: str, /) -> dict[str, str]:
    return {
        one_node_match.group("node_id"): one_group_match.group("group_title")
        for one_group_match in _GROUP_BLOCK_PATTERN.finditer(rendered_diagram)
        for one_node_match in _DEFINED_NODE_PATTERN.finditer(one_group_match.group("group_body"))
    }


@pytest.mark.parametrize(("expected_node_id", "expected_group"), _EXPECTED_GROUP_OF_NODE)
def test_node_is_drawn_inside_its_group(expected_node_id: str, expected_group: str) -> None:
    assert _collect_group_of_every_node(_render(_SHOWCASE_SETTINGS)).get(expected_node_id) == expected_group


def test_every_node_but_service_is_grouped() -> None:
    rendered_diagram: typing.Final = _render(_SHOWCASE_SETTINGS)
    all_defined_ids: typing.Final = {
        one_match.group("node_id") for one_match in _DEFINED_NODE_PATTERN.finditer(rendered_diagram)
    }
    assert all_defined_ids == set(_collect_group_of_every_node(rendered_diagram))
    assert rendered_diagram.split("\n")[0].strip().startswith(_SERVICE_NODE_ID)


def test_group_titles_match_the_registry() -> None:
    assert set(_collect_group_of_every_node(_render(_SHOWCASE_SETTINGS)).values()) == {
        one_node_group.value for one_node_group in diagram_model.NodeGroup
    }


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, _ALL_DIAGRAM_SETTINGS)
def test_group_blocks_are_well_formed(arch_settings: SettingsForFastarch) -> None:
    rendered_diagram: typing.Final = _render(arch_settings)
    all_lines: typing.Final = [one_line.strip() for one_line in rendered_diagram.split("\n")]
    all_group_openings: typing.Final = [one_line for one_line in all_lines if one_line.startswith(_GROUP_OPENING_MARK)]
    all_defined_ids: typing.Final = [
        one_match.group("node_id") for one_match in _DEFINED_NODE_PATTERN.finditer(rendered_diagram)
    ]
    all_drawn_ids: typing.Final = {
        one_node_id
        for one_match in _EDGE_ENDS_PATTERN.finditer(rendered_diagram)
        for one_node_id in (one_match.group("source"), one_match.group("target"))
    }
    assert all_group_openings
    assert len(all_group_openings) == len(set(all_group_openings)) == all_lines.count(_GROUP_CLOSING_LINE)
    assert len(all_defined_ids) == len(set(all_defined_ids))
    assert all_drawn_ids <= set(all_defined_ids) | {mermaid_syntax.render_service_node_id(arch_settings.service_name)}


def test_every_edge_touches_the_service() -> None:
    all_edge_lines: typing.Final = [
        one_line for one_line in _render(_SHOWCASE_SETTINGS).split("\n") if _EDGE_ARROW in one_line
    ]
    assert all_edge_lines
    assert all(_SERVICE_NODE_ID in one_edge_line for one_edge_line in all_edge_lines)
