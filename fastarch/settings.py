import pathlib
import re as py_re
import typing


FILES_SEARCH_PATTERN: typing.Final = "*.py"
MAX_WORKERS: typing.Final = 10
SHIFT_LEFT: typing.Final = " " * 4
VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION: typing.Final = 3
EXTERNAL_CLIENT_TITLE_FOR_SCHEMA: typing.Final = "User/Client"
EXTERNAL_CLIENT_NODE_ID: typing.Final = "external_client"
EXTERNAL_API_TITLE_FOR_SCHEMA: typing.Final = "External API"
EXTERNAL_API_NODE_ID: typing.Final = "External_API"
DIAGRAM_HEADER: typing.Final = "graph TB"
FALLBACK_SERVICE_NODE_ID: typing.Final = "fastarch_service"
TYPICAL_RE_FLAGS: typing.Final = py_re.IGNORECASE | py_re.MULTILINE | py_re.UNICODE | py_re.DOTALL
DEFAULT_PATH: typing.Final = "/docs/architecture/"
DEFAULT_ROOT_DIR: typing.Final = pathlib.Path()
DEFAULT_SERVICE_NAME: typing.Final = "example-service"
UI_PLACEHOLDER_PATTER: typing.Final = py_re.compile(
    r"(?P<pre_open><pre[^>]*>)(?P<pre_body>.*?)(?P<pre_close></pre>)",
    flags=TYPICAL_RE_FLAGS,
)
UI_HTML_TEMPLATE: typing.Final = " ".join(
    pathlib.Path(__file__).parent.joinpath("template.html").read_text().strip().split(),
)
