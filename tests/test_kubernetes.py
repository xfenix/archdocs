import types
import typing

import pytest

from archdocs.main import SettingsForArchdocs
from tests import diagram_rendering


_FIXTURE_ANNOTATIONS: typing.Final = "replicas 3, HPA 2-10, target CPU 70%, cpu 100m-500m, RAM 128Mi-512Mi, GPU 1"
_STATEFULSET_ANNOTATIONS: typing.Final = "StatefulSet, replicas 2, HPA 2-6, target CPU 80%, cpu 250m-1, RAM 256Mi-1Gi"
_ALL_MANIFEST_CASES: typing.Final = types.MappingProxyType(
    {
        "chart of the project": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.TESTS_ROOT / "kubernetes_fixtures", service_name="kubernetes-svc"
            ),
            (
                f'kubernetes_svc{{"kubernetes-svc ({_FIXTURE_ANNOTATIONS})"}}',
                'external_client --> |"HTTPS api.example.com"| kubernetes_svc',
            ),
            (),
        ),
        "manifests and code on one node": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.LITESTAR_ROOT,
                service_name="merged-svc",
                kubernetes_dir=diagram_rendering.TESTS_ROOT / "kubernetes_fixtures" / "chart",
            ),
            (
                f'merged_svc{{"merged-svc ({_FIXTURE_ANNOTATIONS})"}}',
                'external_client --> |"HTTPS api.example.com"| merged_svc',
                'ConfigMap_app_config --> |"env"| merged_svc',
                'Secret_app_secrets --> |"env"| merged_svc',
                'ConfigMap_app_tuning --> |"volume"| merged_svc',
                'merged_svc --> |"volume 10Gi"| PersistentVolume',
                'redisdb["redis"]',
            ),
            (),
        ),
        "disabled toggles": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name="disabled-svc",
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "disabled",
            ),
            ('disabled_svc{"disabled-svc (replicas 2)"}',),
            ("never.example.com", "Ingress", "HPA", "PersistentVolume"),
        ),
        # The second host spells its own name with quotes: a label carrying one closes the edge
        # early and takes the whole diagram down with it, so the quote may not reach the page.
        "ingress without its own tls": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name="plain-svc",
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "plain_ingress",
            ),
            (
                'plain_svc{"plain-svc (replicas 1, cpu 50m)"}',
                'external_client --> |"HTTP plain.example.com"| plain_svc',
                'external_client --> |"HTTP quoted.example.com"| plain_svc',
            ),
            ("HTTPS", '"example"'),
        ),
        "load balancer entrypoint": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name="entry-svc",
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "loadbalancer",
            ),
            ('external_client --> |"LoadBalancer, port 8080"| entry_svc',),
            (),
        ),
        "node port entrypoint": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name="entry-svc",
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "nodeport",
            ),
            (
                'entry_svc{"entry-svc (RAM up to 512Mi)"}',
                'external_client --> |"NodePort"| entry_svc',
                'entry_svc --> |"volume 5Gi"| PersistentVolume',
            ),
            (),
        ),
        "ingress entrypoint": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name="entry-svc",
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "bare_ingress",
            ),
            ('external_client --> |"Ingress"| entry_svc',),
            (),
        ),
        "plain manifests without a chart": (
            SettingsForArchdocs(
                root_dir=diagram_rendering.FASTAPI_ROOT,
                service_name="stateful-svc",
                kubernetes_dir=diagram_rendering.KUBERNETES_VARIANTS_ROOT / "statefulset",
            ),
            (
                f'stateful_svc{{"stateful-svc ({_STATEFULSET_ANNOTATIONS})"}}',
                'external_client --> |"NodePort, port 8080"| stateful_svc',
                'Secret_stateful_secrets --> |"env"| stateful_svc',
                'stateful_svc --> |"volume 20Gi"| PersistentVolume',
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
