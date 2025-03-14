import enum
import typing
from re import py_re

from .parse import http_api, messaging_queue


class FeaturesEnum(enum.Enum):
    fastapi = 1
    faststream = 2
    sqlalchemy = 3


SHIFT_LEFT: typing.Final = " " * 4
TYPICAL_RE_FLAGS: py_re.Pattern = py_re.IGNORECASE | py_re.MULTILINE | py_re.UNICODE
EXTERNAL_CLIENT_SCHEMA: str = "User/Client"
MAP_OF_FEATURES: typing.Final = {
    FeaturesEnum.fastapi: http_api.find_fastapi_features,
    FeaturesEnum.faststream: messaging_queue.find_faststream_features,
}
