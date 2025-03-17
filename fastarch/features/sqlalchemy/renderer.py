import typing

from fastarch import settings
from fastarch.features.sqlalchemy.const import SQLAlchemyFeatures


_VALUE_TO_ILUSTRATE_MASS_CONNECTIONS: typing.Final = 3


def draw_mq_features(service_name: str, features_to_draw: SQLAlchemyFeatures) -> str:
    if not features_to_draw.database_type:
        return ""
    diagram_parts: list[str] = []
    arrow_params: typing.Final = "async" if features_to_draw.async_used else ""
    diagram_parts.extend(
        [
            (
                f"{settings.SHIFT_LEFT}{{{service_name}}} -->|{arrow_params}| "
                f"dbhost ({features_to_draw.database_type}) {one_host!s}"
            )
            for one_host in range(
                _VALUE_TO_ILUSTRATE_MASS_CONNECTIONS
                if features_to_draw.multiple_hosts and features_to_draw.pooling_used
                else 1,
            )
        ]
        * (_VALUE_TO_ILUSTRATE_MASS_CONNECTIONS if features_to_draw.pooling_used else 1),  # many arrows symbols pooling
    )
    return "\n".join(diagram_parts)
