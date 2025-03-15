import typing
from re import py_re


SHIFT_LEFT: typing.Final = " " * 4
EXTERNAL_CLIENT_SCHEMA: typing.Final = "User/Client"
TYPICAL_RE_FLAGS: py_re.Pattern = py_re.IGNORECASE | py_re.MULTILINE | py_re.UNICODE
