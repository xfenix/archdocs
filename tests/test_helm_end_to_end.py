import pathlib
import typing

from fastarch import mermaid_syntax
from fastarch.main import SettingsForFastarch
from tests.served_page import render_architecture_page


_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_HELM_FIXTURES_ROOT: typing.Final = _TESTS_ROOT / "helm_fixtures"
_VARIANTS_ROOT: typing.Final = _TESTS_ROOT / "helm_variants"
_FIXTURE_ANNOTATIONS: typing.Final = ("replicas 3", "HPA 2-10", "target CPU 70%")


def test_chart_features_reach_the_page() -> None:
    expected_node: typing.Final = mermaid_syntax.render_service_node_definition(
        "helm-svc",
        _FIXTURE_ANNOTATIONS,
    ).strip()
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(root_dir=_HELM_FIXTURES_ROOT, service_name="helm-svc"),
    )
    assert "HTTPS api.example.com" in response_text
    assert expected_node in response_text


def test_helm_and_code_share_one_node() -> None:
    expected_node: typing.Final = mermaid_syntax.render_service_node_definition(
        "merged-svc",
        _FIXTURE_ANNOTATIONS,
    ).strip()
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_TESTS_ROOT / "litestar",
            service_name="merged-svc",
            helm_chart_dir=_HELM_FIXTURES_ROOT / "chart",
        ),
    )
    assert "HTTPS api.example.com" in response_text
    assert "redisdb" in response_text
    assert expected_node in response_text


def test_disabled_toggles_win_over_templates() -> None:
    expected_node: typing.Final = mermaid_syntax.render_service_node_definition(
        "disabled-svc",
        ("replicas 2",),
    ).strip()
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_TESTS_ROOT / "fastapi",
            service_name="disabled-svc",
            helm_chart_dir=_VARIANTS_ROOT / "disabled",
        ),
    )
    assert "never.example.com" not in response_text
    assert "Ingress" not in response_text
    assert "HPA" not in response_text
    assert expected_node in response_text


def test_ingress_without_own_tls_stays_http() -> None:
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_TESTS_ROOT / "fastapi",
            service_name="plain-svc",
            helm_chart_dir=_VARIANTS_ROOT / "plain_ingress",
        ),
    )
    assert "HTTP plain.example.com" in response_text
    assert "HTTPS" not in response_text


def test_load_balancer_is_the_entrypoint() -> None:
    expected_node: typing.Final = mermaid_syntax.render_service_node_definition("lb-svc", ("replicas 5",)).strip()
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_TESTS_ROOT / "fastapi",
            service_name="lb-svc",
            helm_chart_dir=_VARIANTS_ROOT / "loadbalancer",
        ),
    )
    assert "LoadBalancer" in response_text
    assert expected_node in response_text
