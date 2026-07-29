import typing

from fastarch import mermaid_syntax, settings
from fastarch.features.app_servers.const import ApplicationServerFeatures


_SINGLE_WORKER_COUNT: typing.Final = 1


def _render_workers_label(workers_count: int, /) -> str:
    if not workers_count:
        return ""
    if workers_count == _SINGLE_WORKER_COUNT:
        return "single worker"
    return f"{workers_count} workers"


def render_application_server_features(service_node_id: str, features_to_draw: ApplicationServerFeatures, /) -> str:
    if not features_to_draw.servers_used:
        return ""
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
    return mermaid_syntax.render_edge(
        settings.EXTERNAL_CLIENT_NODE_ID,
        f"Served by {properties_on_arrow}",
        service_node_id,
    )
