import typing

from fastarch import settings
from fastarch.features.sqlalchemy.const import SQLAlchemyFeatures


_VALUE_TO_ILUSTRATE_MASS_CONNECTIONS: typing.Final = 3


def draw_sqlalchemy_features(service_name: str, features_to_draw: SQLAlchemyFeatures) -> str:
    if not features_to_draw.connection_type and not features_to_draw.async_used and not features_to_draw.retry_used:
        return ""
    diagram_parts: list[str] = []
    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                "async" if features_to_draw.async_used else "",
                features_to_draw.database_type,
                features_to_draw.target_session_attrs,
            ],
        ),
    )
    diagram_parts.extend(
        (
            f"{settings.SHIFT_LEFT}{{{service_name}}} --> |{properties_on_arrow}| "
            f"{features_to_draw.database_type}db{counter if features_to_draw.multiple_hosts else ""}"
        )
        for counter in range(_VALUE_TO_ILUSTRATE_MASS_CONNECTIONS if features_to_draw.pooling_used else 1)
    )
    return "\n".join(diagram_parts)
