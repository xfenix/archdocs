import typing

from fastarch import mermaid_syntax
from fastarch.features.http_clients.const import HttpClientFeatures


def render_http_client_features(service_node_id: str, features_to_draw: HttpClientFeatures, /) -> str:
    if not features_to_draw.has_external_calls or not features_to_draw.clients_used:
        return ""

    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                "async" if features_to_draw.async_used else "",
                ", ".join(sorted(features_to_draw.clients_used)),
            ],
        ),
    )

    return mermaid_syntax.render_edge(service_node_id, f"HTTP ({properties_on_arrow})", "External_API")
