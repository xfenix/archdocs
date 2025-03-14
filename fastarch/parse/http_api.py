import dataclasses
import re as py_re
import typing

from fastarch import base


_IN_PATTERN: typing.Final = py_re.compile(r"@(?:\w+\.)?(post|put|patch|delete)\b", flags=base.TYPICAL_RE_FLAGS)
_OUT_PATTERN: typing.Final = py_re.compile(r"@(?:\w+\.)?(get|head|options|trace)\b", flags=base.TYPICAL_RE_FLAGS)


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HTTPApiFeatures:
    in_methods: list[str]
    out_methods: list[str]
    in_methods_existed: bool
    out_methods_existed: bool


def find_fastapi_and_litestar_features(raw_source: str) -> HTTPApiFeatures:
    in_methods: set[str] = set()
    out_methods: set[str] = set()
    if ("from fastapi" not in raw_source and "import fastapi" not in raw_source) and (
        "from litestar" not in raw_source and "import litestar" not in raw_source
    ):
        return HTTPApiFeatures(
            in_methods=in_methods,
            out_methods=out_methods,
            in_methods_existed=False,
            out_methods_existed=False,
        )
    in_methods.update(_IN_PATTERN.findall(raw_source))
    out_methods.update(_OUT_PATTERN.findall(raw_source))
    return HTTPApiFeatures(
        in_methods=list(in_methods),
        out_methods=list(out_methods),
        in_methods_existed=bool(in_methods),
        out_methods_existed=bool(out_methods),
    )


def draw_http_api_features(features_to_draw: HTTPApiFeatures, service_name: str) -> str:
    diagram_parts: list[str] = []
    if features_to_draw.in_methods_existed:
        diagram_parts.append(
            f"{base.SHIFT_LEFT}{base.EXTERNAL_CLIENT_SCHEMA} --> "
            f"|REST ({', '.join(features_to_draw.in_methods)});| {{{service_name}}}"
        )
    if features_to_draw.out_methods_existed:
        diagram_parts.append(
            f"{base.SHIFT_LEFT}{base.EXTERNAL_CLIENT_SCHEMA} <-- "
            f"|REST ({', '.join(features_to_draw.out_methods)});| {{{service_name}}}"
        )
    return "\n".join(diagram_parts)
