import typing

from archdocs import diagram_model
from archdocs.features.kubernetes import const


_INGRESS_ENTRYPOINT_LABEL: typing.Final = "Ingress"
_SECURE_SCHEME: typing.Final = "HTTPS"
_PLAIN_SCHEME: typing.Final = "HTTP"
_PERSISTENT_VOLUME_NODE: typing.Final = diagram_model.build_diagram_node(
    "PersistentVolume",
    "Persistent volume",
    diagram_model.NodeGroup.data_stores,
)


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


def _render_traffic_edges(
    service_node: diagram_model.DiagramNode,
    traffic_to_draw: const.TrafficFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if traffic_to_draw.ingress_enabled and traffic_to_draw.ingress_hosts:
        ingress_scheme: typing.Final = _SECURE_SCHEME if traffic_to_draw.ingress_tls_enabled else _PLAIN_SCHEME
        return tuple(
            diagram_model.DiagramEdge(
                source_node=diagram_model.EXTERNAL_CLIENT_NODE,
                target_node=service_node,
                edge_label=f"{ingress_scheme} {one_ingress_host}",
            )
            for one_ingress_host in traffic_to_draw.ingress_hosts
        )
    entrypoint_label: typing.Final = _render_entrypoint_label(traffic_to_draw)
    if not entrypoint_label:
        return ()
    return (
        diagram_model.DiagramEdge(
            source_node=diagram_model.EXTERNAL_CLIENT_NODE,
            target_node=service_node,
            edge_label=entrypoint_label,
        ),
    )


def _render_configuration_edges(
    service_node: diagram_model.DiagramNode,
    all_configuration_sources: tuple[const.ConfigurationSource, ...],
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    return tuple(
        diagram_model.DiagramEdge(
            source_node=diagram_model.build_diagram_node(
                f"{one_source.source_kind} {one_source.source_name}",
                f"{one_source.source_name} ({one_source.source_kind})",
                diagram_model.NodeGroup.configuration,
            ),
            target_node=service_node,
            edge_label=one_source.attachment_kind,
        )
        for one_source in all_configuration_sources
    )


def _render_storage_edges(
    service_node: diagram_model.DiagramNode,
    resources_to_draw: const.ResourceFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if not resources_to_draw.persistence_enabled:
        return ()
    storage_label: typing.Final = " ".join(
        filter(None, (const.VOLUME_ATTACHMENT, resources_to_draw.persistence_size)),
    )
    return (
        diagram_model.DiagramEdge(
            source_node=service_node,
            target_node=_PERSISTENT_VOLUME_NODE,
            edge_label=storage_label,
        ),
    )


def render_kubernetes_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: const.KubernetesFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    return (
        *_render_traffic_edges(service_node, features_to_draw.traffic_features),
        *_render_configuration_edges(service_node, features_to_draw.configuration_sources),
        *_render_storage_edges(service_node, features_to_draw.resource_features),
    )
