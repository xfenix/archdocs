from experimental.fastarch import settings

from fastarch.parsing.http_api import HTTPApiFeatures


def draw_http_api_features(features_to_draw: HTTPApiFeatures, service_name: str) -> str:
    diagram_parts: list[str] = []
    if features_to_draw.in_methods_existed:
        diagram_parts.append(
            f"{settings.SHIFT_LEFT}{settings.EXTERNAL_CLIENT_SCHEMA} --> "
            f"|REST ({', '.join(features_to_draw.in_methods)});| {{{service_name}}}"
        )
    if features_to_draw.out_methods_existed:
        diagram_parts.append(
            f"{settings.SHIFT_LEFT}{settings.EXTERNAL_CLIENT_SCHEMA} <-- "
            f"|REST ({', '.join(features_to_draw.out_methods)});| {{{service_name}}}"
        )
    return "\n".join(diagram_parts)
