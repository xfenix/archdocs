import pathlib
import typing

import pytest

from fastarch import settings
from fastarch.main import SettingsForFastarch
from tests.served_page import extract_diagram, render_architecture_page


# The service name used to reach the diagram once, as the label of a node whose id was a
# fixed `fastarch_service`, so every edge named the constant and the name was nowhere to
# be seen in the mermaid source. Expected ids are spelled out here on purpose: deriving
# them with the code under test would assert nothing.
_LITESTAR_ROOT: typing.Final = pathlib.Path(__file__).parent / "litestar"
# The node label carries whatever the manifests say about the service, and the lookup climbs out
# of `litestar/` into `tests/` where the fixture charts live. Pinning it to a manifest-less
# directory keeps these expectations about ids and labels alone.
_WITHOUT_MANIFESTS: typing.Final = _LITESTAR_ROOT / "src"
_EDGE_ARROW: typing.Final = " --> "
_SYMBOL_ONLY_NAME: typing.Final = "!!!"
_MARKED_UP_NODE_ENDING: typing.Final = '{"svc<b>&x"}'
# The service and its side groups live one level down, inside the borderless row that turns
# the middle of the page sideways, so every expectation here counts that level in.
_ROW_SHIFT_LEFT: typing.Final = settings.SHIFT_LEFT * 2
_GROUPED_SHIFT_LEFT: typing.Final = settings.SHIFT_LEFT * 3
_SERVICE_ROW_OPENING: typing.Final = f'{settings.SHIFT_LEFT}subgraph service_row[" "]'
_ROW_DIRECTION_LINE: typing.Final = f"{_ROW_SHIFT_LEFT}direction LR"
_INBOUND_GROUP_OPENING: typing.Final = f'{_ROW_SHIFT_LEFT}subgraph group_inbound_api["Inbound API"]'
_EXTERNAL_CLIENT_DEFINITION: typing.Final = f'{_GROUPED_SHIFT_LEFT}external_client["User/Client"]'


def _render_diagram(service_name: str) -> str:
    return extract_diagram(
        render_architecture_page(
            SettingsForFastarch(
                root_dir=_LITESTAR_ROOT,
                service_name=service_name,
                kubernetes_dir=_WITHOUT_MANIFESTS,
            ),
        ),
    )


def _render_node_definition(expected_node_id: str, service_name: str) -> str:
    return f'{_ROW_SHIFT_LEFT}{expected_node_id}{{"{service_name}"}}'


def _extract_edge_lines(all_diagram_lines: list[str]) -> list[str]:
    return [one_line for one_line in all_diagram_lines if _EDGE_ARROW in one_line]


@pytest.mark.parametrize(
    ("service_name", "expected_node_id"),
    [("payments-api", "payments_api"), ("svc.v2", "svc_v2"), ("Billing Service", "Billing_Service")],
)
def test_service_name_is_the_node_id(service_name: str, expected_node_id: str) -> None:
    all_lines: typing.Final = _render_diagram(service_name).split("\n")
    all_edge_lines: typing.Final = _extract_edge_lines(all_lines)
    assert _render_node_definition(expected_node_id, service_name) in all_lines
    assert settings.FALLBACK_SERVICE_NODE_ID not in "\n".join(all_lines)
    assert all(expected_node_id in one_edge_line for one_edge_line in all_edge_lines)


def test_node_id_falls_back_for_symbol_name() -> None:
    all_lines: typing.Final = _render_diagram(_SYMBOL_ONLY_NAME).split("\n")
    all_edge_lines: typing.Final = _extract_edge_lines(all_lines)
    assert _render_node_definition(settings.FALLBACK_SERVICE_NODE_ID, _SYMBOL_ONLY_NAME) in all_lines
    assert any(settings.FALLBACK_SERVICE_NODE_ID in one_edge_line for one_edge_line in all_edge_lines)


def test_external_client_sits_left_of_the_service() -> None:
    all_lines: typing.Final = _render_diagram("client-svc").split("\n")
    all_edge_lines: typing.Final = _extract_edge_lines(all_lines)
    assert all_lines[:4] == [
        _SERVICE_ROW_OPENING,
        _ROW_DIRECTION_LINE,
        _INBOUND_GROUP_OPENING,
        _EXTERNAL_CLIENT_DEFINITION,
    ]
    assert all_lines.index(_EXTERNAL_CLIENT_DEFINITION) < all_lines.index(
        _render_node_definition("client_svc", "client-svc"),
    )
    assert settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA not in "\n".join(all_edge_lines)
    assert any(settings.EXTERNAL_CLIENT_NODE_ID in one_edge_line for one_edge_line in all_edge_lines)


def test_markup_characters_reach_mermaid_intact() -> None:
    page_html: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_LITESTAR_ROOT,
            service_name="svc<b>&x",
            kubernetes_dir=_WITHOUT_MANIFESTS,
        ),
    )
    all_diagram_lines: typing.Final = extract_diagram(page_html).split("\n")
    assert 'svc&lt;b>&amp;x"}' in page_html
    assert "svc<b>" not in page_html
    assert any(one_line.endswith(_MARKED_UP_NODE_ENDING) for one_line in all_diagram_lines)
