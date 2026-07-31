import types
import typing

import pytest

from fastarch.main import SettingsForFastarch
from tests.rendered_diagram import FASTAPI_ROOT, KUBERNETES_VARIANTS_ROOT, LITESTAR_ROOT, TESTS_ROOT, render_diagram


# Manifests are the second source of the same diagram: they annotate the service node the code
# already drew, hang configuration and storage around it, and name the entrypoint the cluster
# exposes. Toggles win over templates — a chart that ships an ingress with `enabled: false`
# describes a service nobody reaches from outside.
_FIXTURE_ANNOTATIONS: typing.Final = "replicas 3, HPA 2-10, target CPU 70%, cpu 100m-500m, RAM 128Mi-512Mi, GPU 1"
_ALL_MANIFEST_CASES: typing.Final = types.MappingProxyType(
    {
        "chart of the project": (
            SettingsForFastarch(root_dir=TESTS_ROOT / "kubernetes_fixtures", service_name="kubernetes-svc"),
            (
                f'kubernetes_svc{{"kubernetes-svc ({_FIXTURE_ANNOTATIONS})"}}',
                'external_client --> |"HTTPS api.example.com"| kubernetes_svc',
            ),
            (),
        ),
        "manifests and code on one node": (
            SettingsForFastarch(
                root_dir=LITESTAR_ROOT,
                service_name="merged-svc",
                kubernetes_dir=TESTS_ROOT / "kubernetes_fixtures" / "chart",
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
            SettingsForFastarch(
                root_dir=FASTAPI_ROOT,
                service_name="disabled-svc",
                kubernetes_dir=KUBERNETES_VARIANTS_ROOT / "disabled",
            ),
            ('disabled_svc{"disabled-svc (replicas 2)"}',),
            ("never.example.com", "Ingress", "HPA"),
        ),
        "ingress without its own tls": (
            SettingsForFastarch(
                root_dir=FASTAPI_ROOT,
                service_name="plain-svc",
                kubernetes_dir=KUBERNETES_VARIANTS_ROOT / "plain_ingress",
            ),
            ('external_client --> |"HTTP plain.example.com"| plain_svc',),
            ("HTTPS",),
        ),
        "load balancer entrypoint": (
            SettingsForFastarch(
                root_dir=FASTAPI_ROOT,
                service_name="entry-svc",
                kubernetes_dir=KUBERNETES_VARIANTS_ROOT / "loadbalancer",
            ),
            ('external_client --> |"LoadBalancer, port 8080"| entry_svc',),
            (),
        ),
        "node port entrypoint": (
            SettingsForFastarch(
                root_dir=FASTAPI_ROOT,
                service_name="entry-svc",
                kubernetes_dir=KUBERNETES_VARIANTS_ROOT / "nodeport",
            ),
            ('external_client --> |"NodePort"| entry_svc',),
            (),
        ),
        "ingress entrypoint": (
            SettingsForFastarch(
                root_dir=FASTAPI_ROOT,
                service_name="entry-svc",
                kubernetes_dir=KUBERNETES_VARIANTS_ROOT / "bare_ingress",
            ),
            ('external_client --> |"Ingress"| entry_svc',),
            (),
        ),
        "plain manifests without a chart": (
            SettingsForFastarch(
                root_dir=FASTAPI_ROOT,
                service_name="stateful-svc",
                kubernetes_dir=KUBERNETES_VARIANTS_ROOT / "statefulset",
            ),
            (
                'stateful_svc{"stateful-svc (StatefulSet, replicas 2, cpu 250m-1, RAM 256Mi-1Gi)"}',
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
    arch_settings: SettingsForFastarch,
    expected_parts: tuple[str, ...],
    forbidden_parts: tuple[str, ...],
) -> None:
    rendered_diagram: typing.Final = render_diagram(arch_settings)

    for one_expected_part in expected_parts:
        assert one_expected_part in rendered_diagram, one_expected_part
    for one_forbidden_part in forbidden_parts:
        assert one_forbidden_part not in rendered_diagram, one_forbidden_part
