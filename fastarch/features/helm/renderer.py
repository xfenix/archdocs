import typing

from fastarch import mermaid_syntax, settings
from fastarch.features.helm.const import (
    LOAD_BALANCER_SERVICE_TYPE,
    NODE_PORT_SERVICE_TYPE,
    HelmChartFeatures,
)


_INGRESS_ENTRYPOINT_LABEL: typing.Final = "Ingress"
_EXPOSED_SERVICE_TYPES: typing.Final = frozenset((LOAD_BALANCER_SERVICE_TYPE, NODE_PORT_SERVICE_TYPE))


def render_helm_node_annotations(features_to_draw: HelmChartFeatures) -> tuple[str, ...]:
    return tuple(
        filter(
            None,
            [
                f"replicas {features_to_draw.replica_count}" if features_to_draw.replica_count else "",
                (
                    f"HPA {features_to_draw.min_replicas}-{features_to_draw.max_replicas}"
                    if features_to_draw.max_replicas
                    else ""
                ),
                (
                    f"target CPU {features_to_draw.target_cpu_utilization}%"
                    if features_to_draw.target_cpu_utilization
                    else ""
                ),
            ],
        ),
    )


def _render_entrypoint_label(features_to_draw: HelmChartFeatures) -> str:
    if features_to_draw.ingress_enabled:
        return _INGRESS_ENTRYPOINT_LABEL
    if features_to_draw.service_type in _EXPOSED_SERVICE_TYPES:
        return features_to_draw.service_type
    return ""


def render_helm_features(features_to_draw: HelmChartFeatures) -> str:
    if features_to_draw.ingress_enabled and features_to_draw.ingress_hosts:
        scheme_on_arrow: typing.Final = "HTTPS" if features_to_draw.ingress_tls_enabled else "HTTP"
        return "\n".join(
            mermaid_syntax.render_edge(
                settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA,
                f"{scheme_on_arrow} {one_ingress_host}",
                settings.SERVICE_NODE_ID,
            )
            for one_ingress_host in features_to_draw.ingress_hosts
        )
    entrypoint_label: typing.Final = _render_entrypoint_label(features_to_draw)
    if not entrypoint_label:
        return ""
    return mermaid_syntax.render_edge(
        settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA,
        entrypoint_label,
        settings.SERVICE_NODE_ID,
    )
