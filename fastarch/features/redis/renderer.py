import typing

from fastarch.features.redis.const import RedisFeatures


_VALUE_TO_ILUSTRATE_MASS_CONNECTIONS: typing.Final = 3


def draw_redis_features(service_name: str, features_to_draw: RedisFeatures) -> str:
    if not features_to_draw.connection_type and not features_to_draw.async_used and not features_to_draw.retry_used:
        return ""
    diagram_parts: list[str] = []
    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                "async" if features_to_draw.async_used else "",
                "retry" if features_to_draw.retry_used else "",
                "sentinel" if features_to_draw.connection_type == "sentinel" else "",
                "cluster" if features_to_draw.connection_type == "cluster" else "",
            ],
        ),
    )
    diagram_parts.extend(
        properties_on_arrow,
    )
    return "\n".join(diagram_parts)
