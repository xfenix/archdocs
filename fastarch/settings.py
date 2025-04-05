import pathlib
import re as py_re
import typing


FILES_SEARCH_PATTERN: typing.Final = "*.py"
MAX_WORKERS: typing.Final = 10
SHIFT_LEFT: typing.Final = " " * 4
VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION: typing.Final = 3
EXTERNAL_CLIENT_TITLE_FOR_SCHEMA: typing.Final = "User/Client"
TYPICAL_RE_FLAGS: typing.Final = py_re.IGNORECASE | py_re.MULTILINE | py_re.UNICODE
DEFAULT_PATH: typing.Final = "/docs/architecture/"
DEFAULT_ROOT_DIR: typing.Final = pathlib.Path()
DEFAULT_SERVICE_NAME: typing.Final = "example-service"
UI_HTML_TEMPLATE: typing.Final = "".join(
    pathlib.Path(__file__).parent.joinpath("template.html").read_text().strip().split(),
)
