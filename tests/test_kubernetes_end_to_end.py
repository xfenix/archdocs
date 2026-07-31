import pathlib
import typing

import pytest

from fastarch.main import SettingsForFastarch
from tests.served_page import extract_diagram, render_architecture_page, render_service_node_definition


_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_FIXTURES_ROOT: typing.Final = _TESTS_ROOT / "kubernetes_fixtures"
_VARIANTS_ROOT: typing.Final = _TESTS_ROOT / "kubernetes_variants"
_FASTAPI_ROOT: typing.Final = _TESTS_ROOT / "fastapi"
_FIXTURE_ANNOTATIONS: typing.Final = (
    "replicas 3",
    "HPA 2-10",
    "target CPU 70%",
    "cpu 100m-500m",
    "RAM 128Mi-512Mi",
    "GPU 1",
)
_MERGED_SETTINGS: typing.Final = SettingsForFastarch(
    root_dir=_TESTS_ROOT / "litestar",
    service_name="merged-svc",
    kubernetes_dir=_FIXTURES_ROOT / "chart",
)


def test_chart_features_reach_the_page() -> None:
    expected_node: typing.Final = render_service_node_definition(
        "kubernetes-svc",
        _FIXTURE_ANNOTATIONS,
    )
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(root_dir=_FIXTURES_ROOT, service_name="kubernetes-svc"),
    )
    assert "HTTPS api.example.com" in response_text
    assert expected_node in response_text


@pytest.mark.parametrize(
    "expected_edge",
    [
        'ConfigMap_app_config --> |"env"| merged_svc',
        'Secret_app_secrets --> |"env"| merged_svc',
        'ConfigMap_app_tuning --> |"volume"| merged_svc',
        'merged_svc --> |"volume 10Gi"| PersistentVolume',
    ],
)
def test_configuration_and_storage_reach_the_page(expected_edge: str) -> None:
    assert expected_edge in extract_diagram(render_architecture_page(_MERGED_SETTINGS))


def test_manifests_and_code_share_one_node() -> None:
    expected_node: typing.Final = render_service_node_definition(
        "merged-svc",
        _FIXTURE_ANNOTATIONS,
    )
    response_text: typing.Final = render_architecture_page(_MERGED_SETTINGS)
    assert "HTTPS api.example.com" in response_text
    assert "redisdb" in response_text
    assert expected_node in response_text


def test_disabled_toggles_win_over_templates() -> None:
    expected_node: typing.Final = render_service_node_definition(
        "disabled-svc",
        ("replicas 2",),
    )
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_FASTAPI_ROOT,
            service_name="disabled-svc",
            kubernetes_dir=_VARIANTS_ROOT / "disabled",
        ),
    )
    assert "never.example.com" not in response_text
    assert "Ingress" not in response_text
    assert "HPA" not in response_text
    assert expected_node in response_text


def test_ingress_without_own_tls_stays_http() -> None:
    response_text: typing.Final = render_architecture_page(
        SettingsForFastarch(
            root_dir=_FASTAPI_ROOT,
            service_name="plain-svc",
            kubernetes_dir=_VARIANTS_ROOT / "plain_ingress",
        ),
    )
    assert "HTTP plain.example.com" in response_text
    assert "HTTPS" not in response_text


@pytest.mark.parametrize(
    ("variant_name", "expected_label"),
    [("loadbalancer", "LoadBalancer, port 8080"), ("nodeport", "NodePort"), ("bare_ingress", "Ingress")],
)
def test_service_is_the_entrypoint(variant_name: str, expected_label: str) -> None:
    rendered_diagram: typing.Final = extract_diagram(
        render_architecture_page(
            SettingsForFastarch(
                root_dir=_FASTAPI_ROOT,
                service_name="entry-svc",
                kubernetes_dir=_VARIANTS_ROOT / variant_name,
            ),
        ),
    )
    assert f'external_client --> |"{expected_label}"| entry_svc' in rendered_diagram


@pytest.mark.parametrize(
    "expected_diagram_part",
    [
        'stateful_svc{"stateful-svc (StatefulSet, replicas 2, cpu 250m-1, RAM 256Mi-1Gi)"}',
        'external_client --> |"NodePort, port 8080"| stateful_svc',
        'Secret_stateful_secrets --> |"env"| stateful_svc',
        'stateful_svc --> |"volume 20Gi"| PersistentVolume',
    ],
)
def test_plain_manifests_are_read_without_a_chart(expected_diagram_part: str) -> None:
    rendered_diagram: typing.Final = extract_diagram(
        render_architecture_page(
            SettingsForFastarch(
                root_dir=_FASTAPI_ROOT,
                service_name="stateful-svc",
                kubernetes_dir=_VARIANTS_ROOT / "statefulset",
            ),
        ),
    )
    assert expected_diagram_part in rendered_diagram
