import typing

from fastarch.features.helm.parser import find_helm_features


_PLAIN_VALUES_SOURCE: typing.Final = """replicaCount: 3

service:
  type: LoadBalancer
  port: 80

ingress:
  enabled: true
  hosts:
    - host: api.example.com
  tls:
    - secretName: api-example-com-tls

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
"""
_TEMPLATED_INGRESS_SOURCE: typing.Final = """apiVersion: networking.k8s.io/v1
kind: Ingress
spec:
  rules:
    - host: {{ .host | quote }}
"""
_EXPECTED_REPLICA_COUNT: typing.Final = 3
_EXPECTED_MIN_REPLICAS: typing.Final = 2
_EXPECTED_MAX_REPLICAS: typing.Final = 10
_EXPECTED_TARGET_CPU: typing.Final = 70


def test_non_chart_source_not_detected() -> None:
    features: typing.Final = find_helm_features("import fastapi\n\napp = fastapi.FastAPI()\n")
    assert not features.chart_detected
    assert not features.ingress_enabled
    assert features.ingress_hosts == ()
    assert features.replica_count == 0
    assert features.service_type == ""


def test_empty_source_not_detected() -> None:
    assert not find_helm_features("").chart_detected


def test_plain_values_parsed() -> None:
    features: typing.Final = find_helm_features(_PLAIN_VALUES_SOURCE)
    assert features.chart_detected
    assert features.ingress_enabled
    assert features.ingress_hosts == ("api.example.com",)
    assert features.ingress_tls_enabled
    assert features.service_type == "LoadBalancer"
    assert features.replica_count == _EXPECTED_REPLICA_COUNT
    assert features.autoscaling_enabled
    assert features.min_replicas == _EXPECTED_MIN_REPLICAS
    assert features.max_replicas == _EXPECTED_MAX_REPLICAS
    assert features.target_cpu_utilization == _EXPECTED_TARGET_CPU


def test_absent_tls_not_reported() -> None:
    features: typing.Final = find_helm_features("replicaCount: 1\ningress:\n  enabled: true\n  tls: []\n")
    assert features.ingress_enabled
    assert not features.ingress_tls_enabled


def test_disabled_ingress_not_reported() -> None:
    features: typing.Final = find_helm_features("replicaCount: 1\ningress:\n  enabled: false\n")
    assert features.chart_detected
    assert not features.ingress_enabled


def test_hosts_deduped_in_chart_order() -> None:
    features: typing.Final = find_helm_features(
        "replicaCount: 1\ningress:\n  enabled: true\n  hosts:\n"
        "    - host: b.example.com\n    - host: a.example.com\n    - host: b.example.com\n",
    )
    assert features.ingress_hosts == ("b.example.com", "a.example.com")


def test_blocks_do_not_bleed_between_files() -> None:
    features: typing.Final = find_helm_features(f"{_PLAIN_VALUES_SOURCE}\n---\n{_TEMPLATED_INGRESS_SOURCE}")
    # `type:` also appears outside the `service:` block, only the block itself counts.
    assert features.service_type == "LoadBalancer"
    assert features.min_replicas == _EXPECTED_MIN_REPLICAS
    assert features.max_replicas == _EXPECTED_MAX_REPLICAS
    assert features.ingress_hosts == ("api.example.com",)
