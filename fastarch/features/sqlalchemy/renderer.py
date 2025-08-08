import typing

from fastarch import settings
from fastarch.features.sqlalchemy.const import SQLAlchemyFeatures


def draw_sqlalchemy_features(service_name: str, features_to_draw: SQLAlchemyFeatures) -> str:
    if not features_to_draw.database_type:
        return ""
    diagram_parts: typing.Final[list[str]] = []
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
    connections_number: typing.Final = (
        settings.VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION if features_to_draw.pooling_used else 1
    )
    for counter in range(connections_number):
        host_suffix = counter if features_to_draw.multiple_hosts else ""
        diagram_parts.append(
            f"{settings.SHIFT_LEFT}{{{service_name}}} --> |{properties_on_arrow}|"
            f" {features_to_draw.database_type}db{host_suffix}",
        )
    return "\n".join(diagram_parts)
