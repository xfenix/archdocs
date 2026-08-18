import dataclasses
import pathlib
import types
import typing

import hypothesis
import pytest
from hypothesis import strategies as st

from archdocs.main import SettingsForArchdocs
from tests import diagram_rendering, factories, generated_project


_FIXTURE_ANNOTATIONS: typing.Final = "replicas 3, HPA 2-10, target CPU 70%, cpu 100m-500m, RAM 128Mi-512Mi, GPU 1"
_STATEFULSET_ANNOTATIONS: typing.Final = "StatefulSet, replicas 2, HPA 2-6, target CPU 80%, cpu 250m-1, RAM 256Mi-1Gi"
_GENERATED_EXAMPLES: typing.Final = 20
_SOURCES_DIR_NAME: typing.Final = "src"
_CHART_RELATIVE_PATH: typing.Final = "deploy/chart"
_CHART_BLUEPRINT: typing.Final = factories.ChartBlueprintFactory.build()
_SERVICE_CONNECTIONS: typing.Final = factories.ServiceConnectionsFactory.build()
_SMALLEST_COUNT: typing.Final = 1
_LARGEST_COUNT: typing.Final = 999
_FULL_UTILIZATION: typing.Final = 100
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


# The fixture charts prove the numbers of one chart somebody wrote; a generated one proves they
# are the chart's numbers at all, and not a fixture the expectations were fitted to.
@hypothesis.settings(
    deadline=None,
    max_examples=_GENERATED_EXAMPLES,
    suppress_health_check=[hypothesis.HealthCheck.function_scoped_fixture],
)
@hypothesis.given(
    replica_count=st.integers(min_value=_SMALLEST_COUNT, max_value=_LARGEST_COUNT),
    min_replicas=st.integers(min_value=_SMALLEST_COUNT, max_value=_LARGEST_COUNT),
    max_replicas=st.integers(min_value=_SMALLEST_COUNT, max_value=_LARGEST_COUNT),
    target_cpu_utilization=st.integers(min_value=_SMALLEST_COUNT, max_value=_FULL_UTILIZATION),
)
def test_generated_chart_reaches_the_diagram(
    tmp_path: pathlib.Path,
    replica_count: int,
    min_replicas: int,
    max_replicas: int,
    target_cpu_utilization: int,
) -> None:
    chart_blueprint: typing.Final = dataclasses.replace(
        _CHART_BLUEPRINT,
        replica_count=replica_count,
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        target_cpu_utilization=target_cpu_utilization,
    )
    source_dir: typing.Final = tmp_path / _SOURCES_DIR_NAME
    source_dir.mkdir(exist_ok=True)
    generated_project.write_service_sources(source_dir, (), _SERVICE_CONNECTIONS)

    rendered_diagram: typing.Final = diagram_rendering.render_diagram(
        factories.SettingsFactory.build(
            root_dir=source_dir,
            service_name=_SERVICE_CONNECTIONS.service_name,
            kubernetes_dir=generated_project.write_generated_chart(
                tmp_path / _CHART_RELATIVE_PATH,
                chart_blueprint,
            ),
        ),
    )

    expected_annotations: typing.Final = ", ".join(
        (
            f"replicas {replica_count}",
            f"HPA {min_replicas}-{max_replicas}",
            f"target CPU {target_cpu_utilization}%",
            f"cpu {chart_blueprint.requested_cpu}-{chart_blueprint.limited_cpu}",
            f"RAM {chart_blueprint.requested_memory}-{chart_blueprint.limited_memory}",
        ),
    )
    assert f'{{"{_SERVICE_CONNECTIONS.service_name} ({expected_annotations})"}}' in rendered_diagram
    assert f'external_client --> |"HTTPS {chart_blueprint.ingress_host}"|' in rendered_diagram
    assert f'["{chart_blueprint.config_map_name} (ConfigMap)"]' in rendered_diagram
    assert f'["{chart_blueprint.secret_name} (Secret)"]' in rendered_diagram
    assert f'|"volume {chart_blueprint.storage_size}"|' in rendered_diagram
    # An ingress is the way in, so the service type behind it is not; and a value a Secret
    # carries is not architecture at all — the page is read by everyone the diagram is for.
    assert f"port {chart_blueprint.service_port}" not in rendered_diagram
    assert chart_blueprint.secret_value not in rendered_diagram
