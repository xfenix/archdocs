import re as py_re
import typing

from archdocs import prefilter, settings
from archdocs.features.http_api.const import HTTPApiFeatures


# A route decorator is called with a path literal (possibly empty, possibly an f-string) or with
# nothing at all: anything looser counts `@mock.patch("src.payments")` in a test file that also
# imports a TestClient as REST traffic. Paths passed as `path=` keywords slip away — that trade
# is taken knowingly.
_SERVED_METHOD_PATTERN: typing.Final = py_re.compile(
    r"@(?:\w+\.)?(post|put|patch|delete|get|head|options|trace)\s*\(\s*(?:\)|[frbu]{0,2}[\"'](?:/|[\"']))",
    flags=settings.TYPICAL_RE_FLAGS,
)
# A decorated method alone says nothing — every router library spells them the same way — so the
# framework has to be imported in the very file the route is written in.
_FRAMEWORK_IMPORT_PATTERN: typing.Final = py_re.compile(
    r"\b(?:from|import)\s+(?:fastapi|litestar)\b",
    flags=settings.TYPICAL_RE_FLAGS,
)
_FRAMEWORK_LITERALS: typing.Final = ("fastapi", "litestar")
_EMPTY_FEATURES: typing.Final = HTTPApiFeatures(served_methods=frozenset())


def find_fastapi_and_litestar_features(raw_source: str) -> HTTPApiFeatures:
    if not prefilter.contains_any_literal(raw_source.lower(), _FRAMEWORK_LITERALS):
        return _EMPTY_FEATURES
    if not _FRAMEWORK_IMPORT_PATTERN.search(raw_source):
        return _EMPTY_FEATURES
    return HTTPApiFeatures(served_methods=frozenset(_SERVED_METHOD_PATTERN.findall(raw_source)))
