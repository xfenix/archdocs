import typing

from fastarch import mermaid_syntax, settings
from fastarch.features.http_api.const import HTTPApiFeatures


def render_http_api_features(features_to_draw: HTTPApiFeatures) -> str:
    if not features_to_draw.in_methods_existed and not features_to_draw.out_methods_existed:
        return ""
    diagram_parts: typing.Final[list[str]] = []
    if features_to_draw.in_methods_existed:
        in_methods: typing.Final = ", ".join(sorted(features_to_draw.in_methods))
        diagram_parts.append(
            mermaid_syntax.render_edge(
                settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA,
                f"REST ({in_methods});",
                settings.SERVICE_NODE_ID,
            ),
        )
    if features_to_draw.out_methods_existed:
        out_methods: typing.Final = ", ".join(sorted(features_to_draw.out_methods))
        diagram_parts.append(
            mermaid_syntax.render_edge(
                settings.SERVICE_NODE_ID,
                f"REST ({out_methods});",
                settings.EXTERNAL_CLIENT_TITLE_FOR_SCHEMA,
            ),
        )
    return "\n".join(diagram_parts)
