import typing

from fastarch import settings
from fastarch.features.helm.const import HelmChartFeatures
from fastarch.features.helm.renderer import render_helm_features


_EXPECTED_INGRESS_EDGES: typing.Final = 2


def _build_features(**overrides: typing.Any) -> HelmChartFeatures:  # noqa: ANN401
    return HelmChartFeatures(chart_detected=True, **overrides)


def test_undetected_chart_renders_nothing() -> None:
    assert render_helm_features(HelmChartFeatures(chart_detected=False)) == ""


def test_ingress_with_tls_uses_https() -> None:
    rendered_diagram: typing.Final = render_helm_features(
        _build_features(ingress_enabled=True, ingress_hosts=("api.example.com",), ingress_tls_enabled=True),
    )
    assert "HTTPS api.example.com" in rendered_diagram
    assert settings.SERVICE_NODE_ID in rendered_diagram


def test_ingress_without_tls_uses_http() -> None:
    rendered_diagram: typing.Final = render_helm_features(
        _build_features(ingress_enabled=True, ingress_hosts=("api.example.com",)),
    )
    assert "HTTP api.example.com" in rendered_diagram
    assert "HTTPS" not in rendered_diagram


def test_each_host_gets_its_own_edge() -> None:
    rendered_diagram: typing.Final = render_helm_features(
        _build_features(ingress_enabled=True, ingress_hosts=("a.example.com", "b.example.com")),
    )
    assert len(rendered_diagram.split("\n")) == _EXPECTED_INGRESS_EDGES
    assert "a.example.com" in rendered_diagram
    assert "b.example.com" in rendered_diagram


def test_ingress_without_hosts_is_generic() -> None:
    rendered_diagram: typing.Final = render_helm_features(_build_features(ingress_enabled=True))
    assert "Ingress" in rendered_diagram
    assert settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA in rendered_diagram


def test_cluster_ip_has_no_entrypoint() -> None:
    assert render_helm_features(_build_features(service_type="ClusterIP", replica_count=3)) == ""
