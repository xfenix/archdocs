import typing

from fastarch import settings
from fastarch.features.http_api.const import HTTPApiFeatures


def draw_http_api_features(service_name: str, features_to_draw: HTTPApiFeatures) -> str:
    if not features_to_draw.in_methods_existed and not features_to_draw.out_methods_existed:
        return ""
    diagram_parts: typing.Final[list[str]] = []
    if features_to_draw.in_methods_existed:
        in_methods: typing.Final = ", ".join(features_to_draw.in_methods)
        diagram_parts.append(
            (
                f"{settings.SHIFT_LEFT}{settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA} --> "
                f"|REST ({in_methods});| {{{service_name}}}"
            ),
        )
    if features_to_draw.out_methods_existed:
        out_methods: typing.Final = ", ".join(features_to_draw.out_methods)
        diagram_parts.append(
            (
                f"{settings.SHIFT_LEFT}{settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA} <-- "
                f"|REST ({out_methods});| {{{service_name}}}"
            ),
        )
    return "\n".join(diagram_parts)
