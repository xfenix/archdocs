import typing

from fastarch import settings
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
                features_to_draw.connection_type if features_to_draw.cluster_or_sentinel else "",
            ],
        ),
    )
    diagram_parts.extend(
        (
            f"{settings.SHIFT_LEFT}{{{service_name}}} --> |{properties_on_arrow}| "
            f"redisdb{counter if features_to_draw.cluster_or_sentinel else ""}"
        )
        for counter in range(_VALUE_TO_ILUSTRATE_MASS_CONNECTIONS if features_to_draw.pooling_used else 1)
    )
    return "\n".join(diagram_parts)
