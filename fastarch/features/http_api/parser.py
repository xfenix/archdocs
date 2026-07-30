import re as py_re
import typing

from fastarch import settings
from fastarch.features.http_api.const import HTTPApiFeatures


# Every route the service declares is traffic somebody else sends to it, `get` included: the
# method only says what the caller asks for, never who dials whom. Splitting the verbs into
# incoming and outgoing used to draw the read routes as an arrow leaving the service towards
# its own clients, which reads as the service calling them back.
_SERVED_METHOD_PATTERN: typing.Final = py_re.compile(
    r"@(?:\w+\.)?(post|put|patch|delete|get|head|options|trace)\b",
    flags=settings.TYPICAL_RE_FLAGS,
)


def find_fastapi_and_litestar_features(raw_source: str) -> HTTPApiFeatures:
    if ("from fastapi" not in raw_source and "import fastapi" not in raw_source) and (
        "from litestar" not in raw_source and "import litestar" not in raw_source
    ):
        return HTTPApiFeatures(served_methods=frozenset(), served_methods_existed=False)
    served_methods: typing.Final = frozenset(_SERVED_METHOD_PATTERN.findall(raw_source))
    return HTTPApiFeatures(served_methods=served_methods, served_methods_existed=bool(served_methods))
