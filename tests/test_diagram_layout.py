import pathlib
import types
import typing

import hypothesis
import pytest

from archdocs.main import SettingsForArchdocs
from tests import diagram_parts, diagram_rendering, factories, generated_project


# Mermaid has no coordinates: a diagram is laid out from the direction of its arrows and from
# the order its lines are written in, so both are part of the contract.
_INBOUND_GROUP: typing.Final = "Inbound API"
_OUTBOUND_GROUP: typing.Final = "Outbound calls"
_MESSAGING_GROUP: typing.Final = "Messaging & tasks"
_DATA_STORES_GROUP: typing.Final = "Data stores"
_CONFIGURATION_GROUP: typing.Final = "Configuration"
_SHOWCASE_NODE_ID: typing.Final = "showcase_service"
_GENERATED_EXAMPLES: typing.Final = 25
_SERVICE_CONNECTIONS: typing.Final = factories.ServiceConnectionsFactory.build()
_EXPECTED_SHOWCASE_GROUPS: typing.Final = types.MappingProxyType(
    {
        "external_client": _INBOUND_GROUP,
        "rabbit": _MESSAGING_GROUP,
        "kafka": _MESSAGING_GROUP,
        "nats": _MESSAGING_GROUP,
        "redis": _MESSAGING_GROUP,
        "TaskQueue_Worker": _MESSAGING_GROUP,
        "External_API": _OUTBOUND_GROUP,
        "PersistentVolume": _DATA_STORES_GROUP,
        "redisdb": _DATA_STORES_GROUP,
        "redisdb_cluster0": _DATA_STORES_GROUP,
        "redisdb_cluster1": _DATA_STORES_GROUP,
        "redisdb_cluster2": _DATA_STORES_GROUP,
        "redisdb_sentinel0": _DATA_STORES_GROUP,
        "redisdb_sentinel1": _DATA_STORES_GROUP,
        "redisdb_sentinel2": _DATA_STORES_GROUP,
        "postgresql_asyncpgdb": _DATA_STORES_GROUP,
        "postgresql_psycopgdb0": _DATA_STORES_GROUP,
        "postgresql_psycopgdb1": _DATA_STORES_GROUP,
        "postgresql_psycopgdb2": _DATA_STORES_GROUP,
        "sqlite_aiosqlitedb": _DATA_STORES_GROUP,
        "ConfigMap_app_config": _CONFIGURATION_GROUP,
        "Secret_app_secrets": _CONFIGURATION_GROUP,
        "ConfigMap_app_tuning": _CONFIGURATION_GROUP,
    },
)
_PLACEMENT_ORDER_OF_MARKS: typing.Final = (
    'subgraph group_configuration["Configuration"]',
    'subgraph service_row[" "]',
    "direction LR",
    'subgraph group_inbound_api["Inbound API"]',
    'external_client["User/Client"]',
    'showcase_service{"',
    'subgraph group_messaging_and_tasks["Messaging & tasks"]',
    'subgraph group_outbound_calls["Outbound calls"]',
    "style service_row fill:none,stroke:none",
    'subgraph group_data_stores["Data stores"]',
)
_ALL_SERVICE_NAMES: typing.Final = (
    ("payments-api", "payments_api"),
    ("svc.v2", "svc_v2"),
    ("Billing Service", "Billing_Service"),
    # Only the separators are stripped off the ends: a name may open and close with a letter.
    ("Xray-svc", "Xray_svc"),
    # Whitespace inside a name is the name, and only a line break would end the statement early.
    ("Two  Spaces", "Two_Spaces"),
    ("!!!", "archdocs_service"),
)


def assert_arrows_agree_with_their_side(rendered_diagram: str, /) -> None:
    group_of_node: typing.Final = diagram_parts.collect_group_of_every_node(rendered_diagram)
    all_edge_ends: typing.Final = diagram_parts.collect_edge_ends(rendered_diagram)
    all_target_groups: typing.Final = {group_of_node.get(one_ends.target_id) for one_ends in all_edge_ends}
    all_source_groups: typing.Final = {group_of_node.get(one_ends.source_id) for one_ends in all_edge_ends}
    assert _INBOUND_GROUP not in all_target_groups
    assert _OUTBOUND_GROUP not in all_source_groups


@pytest.mark.parametrize(diagram_rendering.SETTINGS_ARGUMENT, diagram_rendering.ALL_EXAMPLE_SETTINGS)
def test_arrows_agree_with_their_side(arch_settings: SettingsForArchdocs) -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_example_diagram(arch_settings)

    assert diagram_parts.collect_edge_ends(rendered_diagram)
    assert_arrows_agree_with_their_side(rendered_diagram)


# An arrow into an inbound group drags the whole group to the other end of the page, so the
# side a group lands on is decided by every technology the project happens to combine.
@hypothesis.settings(
    deadline=None,
    max_examples=_GENERATED_EXAMPLES,
    suppress_health_check=[hypothesis.HealthCheck.function_scoped_fixture],
)
@hypothesis.given(all_technologies=generated_project.TECHNOLOGY_SUBSET_STRATEGY)
def test_generated_arrows_agree_with_their_side(
    tmp_path: pathlib.Path,
    all_technologies: list[generated_project.OneTechnology],
) -> None:
    assert_arrows_agree_with_their_side(
        diagram_rendering.render_generated_diagram(tmp_path, all_technologies, _SERVICE_CONNECTIONS),
    )


def test_showcase_nodes_sit_in_their_groups() -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_example_diagram(diagram_rendering.SHOWCASE_SETTINGS)

    all_edge_lines: typing.Final = diagram_parts.extract_edge_lines(rendered_diagram)
    assert diagram_parts.collect_group_of_every_node(rendered_diagram) == _EXPECTED_SHOWCASE_GROUPS
    assert all_edge_lines
    assert all(_SHOWCASE_NODE_ID in one_edge_line for one_edge_line in all_edge_lines)


def test_groups_sit_around_the_service() -> None:
    all_lines: typing.Final = [
        one_line.strip()
        for one_line in diagram_rendering.render_example_diagram(diagram_rendering.SHOWCASE_SETTINGS).split("\n")
    ]

    all_positions: typing.Final = [
        next(line_index for line_index, one_line in enumerate(all_lines) if one_line.startswith(one_mark))
        for one_mark in _PLACEMENT_ORDER_OF_MARKS
    ]
    assert all_positions == sorted(all_positions)


@pytest.mark.parametrize(("service_name", "expected_node_id"), _ALL_SERVICE_NAMES)
def test_service_name_becomes_the_node_id(service_name: str, expected_node_id: str) -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_example_diagram(
        diagram_rendering.build_named_settings(service_name),
    )

    all_edge_lines: typing.Final = diagram_parts.extract_edge_lines(rendered_diagram)
    assert f'{expected_node_id}{{"{service_name}"}}' in rendered_diagram
    assert all_edge_lines
    assert all(expected_node_id in one_edge_line for one_edge_line in all_edge_lines)


def test_credentials_never_reach_the_diagram() -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_example_diagram(
        diagram_rendering.build_named_settings("secretive-svc"),
    )

    assert "user:password" not in rendered_diagram
    assert "://***@" in rendered_diagram
