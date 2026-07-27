import pathlib
import typing

import pytest

from fastarch import mermaid_syntax, settings
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


# The service name used to reach the diagram once, as the label of a node whose id was a
# fixed `fastarch_service`, so every edge named the constant and the name was nowhere to be
# seen in the mermaid source. The id is derived from the name again, and the two node titles
# that are not legal mermaid ids travel as quoted labels.
_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_SETTINGS_ARGUMENT: typing.Final = "arch_settings"
_EDGE_ARROW: typing.Final = " --> "
_ALL_DIAGRAM_SETTINGS: typing.Final = (
    SettingsForFastarch(root_dir=_TESTS_ROOT / "fastapi", service_name="fastapi-svc"),
    SettingsForFastarch(root_dir=_TESTS_ROOT / "litestar", service_name="litestar-svc"),
    SettingsForFastarch(root_dir=_TESTS_ROOT / "helm_fixtures", service_name="helm-svc"),
)


def _render(arch_settings: SettingsForFastarch) -> str:
    return ArchitectureParserAndRenderer(local_settings=arch_settings).render_architecture_diagram()


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, _ALL_DIAGRAM_SETTINGS)
def test_service_name_is_the_node_id(arch_settings: SettingsForFastarch) -> None:
    service_node_id: typing.Final = mermaid_syntax.render_service_node_id(arch_settings.service_name)
    all_lines: typing.Final = _render(arch_settings).split("\n")
    assert service_node_id == mermaid_syntax.render_node_id(arch_settings.service_name)
    assert arch_settings.service_name in all_lines[0]
    assert settings.FALLBACK_SERVICE_NODE_ID not in "\n".join(all_lines)
    assert any(_EDGE_ARROW in one_line and service_node_id in one_line for one_line in all_lines)


def test_node_id_falls_back_for_symbol_name() -> None:
    # `render_node_id` can legitimately reduce a name to nothing, and an empty mermaid id is
    # a parse error, so the constant takes over while the label keeps the name as given.
    first_line: typing.Final = _render(
        SettingsForFastarch(root_dir=_TESTS_ROOT / "fastapi", service_name="***"),
    ).split("\n")[0]
    assert first_line == f'{settings.SHIFT_LEFT}{settings.FALLBACK_SERVICE_NODE_ID}{{"***"}}'


@pytest.mark.parametrize(_SETTINGS_ARGUMENT, _ALL_DIAGRAM_SETTINGS)
def test_external_client_is_labelled(arch_settings: SettingsForFastarch) -> None:
    all_lines: typing.Final = _render(arch_settings).split("\n")
    all_edge_lines: typing.Final = [one_line for one_line in all_lines if _EDGE_ARROW in one_line]
    assert settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA not in "\n".join(all_edge_lines)
    assert any(settings.EXTERNAL_CLIENT_NODE_ID in one_edge_line for one_edge_line in all_edge_lines)
    assert all_lines[1] == f'{settings.SHIFT_LEFT}{settings.EXTERNAL_CLIENT_NODE_ID}["User/Client"]'
