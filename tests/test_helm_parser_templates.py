import typing

import hypothesis
from hypothesis import strategies as st

from fastarch.features.helm.parser import find_helm_features


# Helm templates are Go templates first and YAML second, so the parser has to read them
# without ever turning a `{{ ... }}` directive into a value.
_TEMPLATED_SOURCE: typing.Final = """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: templated
spec:
  rules:
    - host: {{ .host | quote }}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: templated
spec:
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
"""
_SERVICE_TYPES: typing.Final = ("LoadBalancer", "NodePort", "ClusterIP", "ExternalName")
_MAX_TESTED_REPLICAS: typing.Final = 999


def test_templated_manifests_signal_only() -> None:
    features: typing.Final = find_helm_features(_TEMPLATED_SOURCE)
    assert features.chart_detected
    assert features.ingress_enabled
    assert features.autoscaling_enabled
    assert features.ingress_hosts == ()
    assert features.replica_count == 0
    assert features.min_replicas == 0
    assert features.max_replicas == 0


def test_templated_values_do_not_leak() -> None:
    features: typing.Final = find_helm_features(_TEMPLATED_SOURCE)
    assert all("{{" not in one_ingress_host for one_ingress_host in features.ingress_hosts)
    assert "{{" not in features.service_type


@hypothesis.given(st.integers(min_value=1, max_value=_MAX_TESTED_REPLICAS))
def test_replica_count_round_trips(replica_count: int) -> None:
    assert find_helm_features(f"replicaCount: {replica_count}\n").replica_count == replica_count


@hypothesis.given(st.sampled_from(_SERVICE_TYPES))
def test_service_type_round_trips(service_type: str) -> None:
    assert find_helm_features(f"replicaCount: 1\nservice:\n  type: {service_type}\n").service_type == service_type


@hypothesis.given(st.from_regex(r"[a-z]{2,8}\.[a-z]{2,8}\.[a-z]{2,3}", fullmatch=True))
def test_ingress_host_round_trips(ingress_host: str) -> None:
    features: typing.Final = find_helm_features(
        f"replicaCount: 1\ningress:\n  enabled: true\n  hosts:\n    - host: {ingress_host}\n",
    )
    assert features.ingress_hosts == (ingress_host,)
