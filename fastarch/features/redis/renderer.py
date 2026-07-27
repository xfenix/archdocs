import typing

from fastarch import mermaid_syntax, settings
from fastarch.features.redis.const import RedisFeatures


def render_redis_features(features_to_draw: RedisFeatures) -> str:
    if not features_to_draw.connection_type and not features_to_draw.async_used and not features_to_draw.retry_used:
        return ""
    diagram_parts: typing.Final[list[str]] = []
    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                "async" if features_to_draw.async_used else "",
                "retry" if features_to_draw.retry_used else "",
                features_to_draw.connection_type if features_to_draw.cluster_or_sentinel else "",
            ],
        ),
    )
    for one_counter in range(settings.VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION):
        db_suffix = one_counter if features_to_draw.cluster_or_sentinel else ""
        diagram_parts.append(
            mermaid_syntax.render_edge(settings.SERVICE_NODE_ID, properties_on_arrow, f"redisdb{db_suffix}"),
        )
    return "\n".join(diagram_parts)
