import typing

from fastarch import settings
from fastarch.features.helm.const import HelmChartFeatures
from fastarch.features.helm.renderer import render_helm_features, render_helm_node_annotations


_TARGET_CPU_UTILIZATION: typing.Final = 70


def _build_features(**overrides: typing.Any) -> HelmChartFeatures:  # noqa: ANN401
    return HelmChartFeatures(chart_detected=True, **overrides)


def test_exposed_service_types_are_entrypoints() -> None:
    assert "LoadBalancer" in render_helm_features(_build_features(service_type="LoadBalancer"))
    assert "NodePort" in render_helm_features(_build_features(service_type="NodePort"))


def test_undetected_chart_has_no_annotations() -> None:
    assert render_helm_node_annotations(HelmChartFeatures(chart_detected=False)) == ()


def test_annotation_order_is_stable() -> None:
    annotations: typing.Final = render_helm_node_annotations(
        _build_features(
            replica_count=3,
            autoscaling_enabled=True,
            min_replicas=2,
            max_replicas=10,
            target_cpu_utilization=_TARGET_CPU_UTILIZATION,
        ),
    )
    assert annotations == ("replicas 3", "HPA 2-10", "target CPU 70%")


def test_autoscaling_without_max_is_skipped() -> None:
    assert render_helm_node_annotations(_build_features(replica_count=2, autoscaling_enabled=True)) == ("replicas 2",)


def test_no_scaling_means_no_annotations() -> None:
    assert render_helm_node_annotations(_build_features(ingress_enabled=True)) == ()


def test_rendered_lines_are_indented() -> None:
    rendered_diagram: typing.Final = render_helm_features(
        _build_features(ingress_enabled=True, ingress_hosts=("a.example.com", "b.example.com")),
    )
    assert all(one_line.startswith(settings.SHIFT_LEFT) for one_line in rendered_diagram.split("\n"))
