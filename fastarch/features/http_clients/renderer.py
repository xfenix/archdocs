import typing

from fastarch import settings
from fastarch.features.http_clients.const import HttpClientFeatures


def draw_http_client_features(service_name: str, features_to_draw: HttpClientFeatures) -> str:
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

    return f"{settings.SHIFT_LEFT}{{{service_name}}} --> |HTTP ({properties_on_arrow})| External_API"
