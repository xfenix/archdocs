import re as py_re
import typing

from fastarch import settings
from fastarch.features.http_api.const import HTTPApiFeatures


_IN_PATTERN: typing.Final = py_re.compile(r"@(?:\w+\.)?(post|put|patch|delete)\b", flags=settings.TYPICAL_RE_FLAGS)
_OUT_PATTERN: typing.Final = py_re.compile(r"@(?:\w+\.)?(get|head|options|trace)\b", flags=settings.TYPICAL_RE_FLAGS)


def find_fastapi_and_litestar_features(raw_source: str) -> HTTPApiFeatures:
    in_methods: typing.Final[set[str]] = set()
    out_methods: typing.Final[set[str]] = set()
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
