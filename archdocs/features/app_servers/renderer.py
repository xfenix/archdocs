import typing

from archdocs import diagram_model
from archdocs.features.app_servers.const import ApplicationServerFeatures


_SINGLE_WORKER_COUNT: typing.Final = 1


def _render_workers_label(workers_count: int, /) -> str:
    if not workers_count:
        return ""
    if workers_count == _SINGLE_WORKER_COUNT:
        return "single worker"
    return f"{workers_count} workers"


def render_application_server_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: ApplicationServerFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if not features_to_draw.servers_used:
        return ()
    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                ", ".join(sorted(features_to_draw.servers_used)),
                _render_workers_label(features_to_draw.workers_count),
                f"port {features_to_draw.listen_port}" if features_to_draw.listen_port else "",
                "TLS" if features_to_draw.tls_enabled else "",
                "HTTP/2" if features_to_draw.http2_enabled else "",
            ],
        ),
    )
    return (
        diagram_model.DiagramEdge(
            source_node=diagram_model.EXTERNAL_CLIENT_NODE,
            target_node=service_node,
            edge_label=f"Served by {properties_on_arrow}",
        ),
    )
