import typing

from fastarch import mermaid_syntax, settings
from fastarch.features.kubernetes import const


_INGRESS_ENTRYPOINT_LABEL: typing.Final = "Ingress"
_PERSISTENT_VOLUME_NODE_ID: typing.Final = "PersistentVolume"
_SECURE_SCHEME: typing.Final = "HTTPS"
_PLAIN_SCHEME: typing.Final = "HTTP"


def _render_amounts(resource_name: str, amounts_to_draw: const.ResourceAmounts, /) -> str:
    if not amounts_to_draw.requested_amount:
        return f"{resource_name} up to {amounts_to_draw.limited_amount}" if amounts_to_draw.limited_amount else ""
    if amounts_to_draw.limited_amount in {"", amounts_to_draw.requested_amount}:
        return f"{resource_name} {amounts_to_draw.requested_amount}"
    return f"{resource_name} {amounts_to_draw.requested_amount}-{amounts_to_draw.limited_amount}"


def render_kubernetes_node_annotations(features_to_draw: const.KubernetesFeatures) -> tuple[str, ...]:
    scaling_to_draw: typing.Final = features_to_draw.scaling_features
    resources_to_draw: typing.Final = features_to_draw.resource_features
    return tuple(
        filter(
            None,
            (
                "" if scaling_to_draw.workload_kind == const.DEFAULT_WORKLOAD_KIND else scaling_to_draw.workload_kind,
                f"replicas {scaling_to_draw.replica_count}" if scaling_to_draw.replica_count else "",
                f"HPA {scaling_to_draw.min_replicas}-{scaling_to_draw.max_replicas}"
                if scaling_to_draw.max_replicas
                else "",
                f"target CPU {scaling_to_draw.target_cpu_utilization}%"
                if scaling_to_draw.target_cpu_utilization
                else "",
                _render_amounts("cpu", resources_to_draw.cpu_amounts),
                _render_amounts("RAM", resources_to_draw.memory_amounts),
                _render_amounts("GPU", resources_to_draw.gpu_amounts),
            ),
        ),
    )


def _render_entrypoint_label(traffic_to_draw: const.TrafficFeatures, /) -> str:
    if traffic_to_draw.ingress_enabled:
        return _INGRESS_ENTRYPOINT_LABEL
    if traffic_to_draw.service_type not in const.EXPOSED_SERVICE_TYPES:
        return ""
    if not traffic_to_draw.service_port:
        return traffic_to_draw.service_type
    return f"{traffic_to_draw.service_type}, port {traffic_to_draw.service_port}"


def _render_traffic_edges(service_node_id: str, traffic_to_draw: const.TrafficFeatures, /) -> str:
    if traffic_to_draw.ingress_enabled and traffic_to_draw.ingress_hosts:
        ingress_scheme: typing.Final = _SECURE_SCHEME if traffic_to_draw.ingress_tls_enabled else _PLAIN_SCHEME
        return "\n".join(
            mermaid_syntax.render_edge(
                settings.EXTERNAL_CLIENT_NODE_ID,
                f"{ingress_scheme} {one_ingress_host}",
                service_node_id,
            )
            for one_ingress_host in traffic_to_draw.ingress_hosts
        )
    entrypoint_label: typing.Final = _render_entrypoint_label(traffic_to_draw)
    if not entrypoint_label:
        return ""
    return mermaid_syntax.render_edge(settings.EXTERNAL_CLIENT_NODE_ID, entrypoint_label, service_node_id)


def _render_configuration_edges(
    service_node_id: str,
    all_configuration_sources: tuple[const.ConfigurationSource, ...],
    /,
) -> str:
    return "\n".join(
        mermaid_syntax.render_edge(
            mermaid_syntax.render_node_id(f"{one_source.source_kind} {one_source.source_name}"),
            one_source.attachment_kind,
            service_node_id,
        )
        for one_source in all_configuration_sources
    )


def _render_storage_edge(service_node_id: str, resources_to_draw: const.ResourceFeatures, /) -> str:
    if not resources_to_draw.persistence_enabled:
        return ""
    storage_label: typing.Final = " ".join(
        filter(None, (const.VOLUME_ATTACHMENT, resources_to_draw.persistence_size)),
    )
    return mermaid_syntax.render_edge(service_node_id, storage_label, _PERSISTENT_VOLUME_NODE_ID)


def render_kubernetes_features(service_node_id: str, features_to_draw: const.KubernetesFeatures, /) -> str:
    return "\n".join(
        filter(
            None,
            (
                _render_traffic_edges(service_node_id, features_to_draw.traffic_features),
                _render_configuration_edges(service_node_id, features_to_draw.configuration_sources),
                _render_storage_edge(service_node_id, features_to_draw.resource_features),
            ),
        ),
    )
