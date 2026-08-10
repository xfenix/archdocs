import types
import typing

import pytest

from archdocs.main import SettingsForArchdocs
from tests import diagram_rendering


_FIXTURE_ANNOTATIONS: typing.Final = "replicas 3, HPA 2-10, target CPU 70%, cpu 100m-500m, RAM 128Mi-512Mi, GPU 1"
# Each case gets its own random name: the node id it collapses to is only ever a hyphen-to-underscore
# swap of it, so the case bodies below stay as readable as the literals they replace.
_CHART_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_CHART_NODE_ID: typing.Final = diagram_rendering.build_expected_node_id(_CHART_SERVICE_NAME)
_MERGED_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_MERGED_NODE_ID: typing.Final = diagram_rendering.build_expected_node_id(_MERGED_SERVICE_NAME)
_DISABLED_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_DISABLED_NODE_ID: typing.Final = diagram_rendering.build_expected_node_id(_DISABLED_SERVICE_NAME)
_PLAIN_INGRESS_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_PLAIN_INGRESS_NODE_ID: typing.Final = diagram_rendering.build_expected_node_id(_PLAIN_INGRESS_SERVICE_NAME)
_LOADBALANCER_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_LOADBALANCER_NODE_ID: typing.Final = diagram_rendering.build_expected_node_id(_LOADBALANCER_SERVICE_NAME)
_NODEPORT_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_NODEPORT_NODE_ID: typing.Final = diagram_rendering.build_expected_node_id(_NODEPORT_SERVICE_NAME)
_BARE_INGRESS_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_BARE_INGRESS_NODE_ID: typing.Final = diagram_rendering.build_expected_node_id(_BARE_INGRESS_SERVICE_NAME)
_STATEFUL_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_STATEFUL_NODE_ID: typing.Final = diagram_rendering.build_expected_node_id(_STATEFUL_SERVICE_NAME)
_ALL_MANIFEST_CASES: typing.Final = types.MappingProxyType(
    {
        "chart of the project": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.TESTS_ROOT / "kubernetes_fixtures", service_name=_CHART_SERVICE_NAME
            ),
            (
                f'{_CHART_NODE_ID}{{"{_CHART_SERVICE_NAME} ({_FIXTURE_ANNOTATIONS})"}}',
                f'external_client --> |"HTTPS api.example.com"| {_CHART_NODE_ID}',
            ),
            (),
        ),
        "manifests and code on one node": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.LITESTAR_ROOT,
                service_name=_MERGED_SERVICE_NAME,
                kubernetes_dir=diagram_rendering.TESTS_ROOT / "kubernetes_fixtures" / "chart",
            ),
            (
                f'{_MERGED_NODE_ID}{{"{_MERGED_SERVICE_NAME} ({_FIXTURE_ANNOTATIONS})"}}',
                f'external_client --> |"HTTPS api.example.com"| {_MERGED_NODE_ID}',
                f'ConfigMap_app_config --> |"env"| {_MERGED_NODE_ID}',
                f'Secret_app_secrets --> |"env"| {_MERGED_NODE_ID}',
                f'ConfigMap_app_tuning --> |"volume"| {_MERGED_NODE_ID}',
                f'{_MERGED_NODE_ID} --> |"volume 10Gi"| PersistentVolume',
                'redisdb["redis"]',
            ),
            (),
        ),
        "disabled toggles": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name=_DISABLED_SERVICE_NAME,
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "disabled",
            ),
            (f'{_DISABLED_NODE_ID}{{"{_DISABLED_SERVICE_NAME} (replicas 2)"}}',),
            ("never.example.com", "Ingress", "HPA"),
        ),
        "ingress without its own tls": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name=_PLAIN_INGRESS_SERVICE_NAME,
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "plain_ingress",
            ),
            (f'external_client --> |"HTTP plain.example.com"| {_PLAIN_INGRESS_NODE_ID}',),
            ("HTTPS",),
        ),
        "load balancer entrypoint": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name=_LOADBALANCER_SERVICE_NAME,
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "loadbalancer",
            ),
            (f'external_client --> |"LoadBalancer, port 8080"| {_LOADBALANCER_NODE_ID}',),
            (),
        ),
        "node port entrypoint": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name=_NODEPORT_SERVICE_NAME,
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "nodeport",
            ),
            (f'external_client --> |"NodePort"| {_NODEPORT_NODE_ID}',),
            (),
        ),
        "ingress entrypoint": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name=_BARE_INGRESS_SERVICE_NAME,
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "bare_ingress",
            ),
            (f'external_client --> |"Ingress"| {_BARE_INGRESS_NODE_ID}',),
            (),
        ),
        "plain manifests without a chart": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name=_STATEFUL_SERVICE_NAME,
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "statefulset",
            ),
            (
                (f'{_STATEFUL_NODE_ID}{{"{_STATEFUL_SERVICE_NAME} '
                f'(StatefulSet, replicas 2, cpu 250m-1, RAM 256Mi-1Gi)"}}'),
                f'external_client --> |"NodePort, port 8080"| {_STATEFUL_NODE_ID}',
                f'Secret_stateful_secrets --> |"env"| {_STATEFUL_NODE_ID}',
                f'{_STATEFUL_NODE_ID} --> |"volume 20Gi"| PersistentVolume',
            ),
            (),
        ),
    },
)


@pytest.mark.parametrize(
    ("arch_settings", "expected_parts", "forbidden_parts"),
    _ALL_MANIFEST_CASES.values(),
    ids=_ALL_MANIFEST_CASES,
)
def test_manifests_reach_the_diagram(
    arch_settings: SettingsForArchdocs,
    expected_parts: tuple[str, ...],
    forbidden_parts: tuple[str, ...],
) -> None:
    rendered_diagram: typing.Final = diagram_rendering.render_example_diagram(arch_settings)

    for one_expected_part in expected_parts:
        assert one_expected_part in rendered_diagram, one_expected_part
    for one_forbidden_part in forbidden_parts:
        assert one_forbidden_part not in rendered_diagram, one_forbidden_part
