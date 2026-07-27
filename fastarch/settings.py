import itertools
import pathlib
import re as py_re
import typing


FILES_SEARCH_PATTERN: typing.Final = "*.py"
MAX_WORKERS: typing.Final = 10
SHIFT_LEFT: typing.Final = " " * 4
VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION: typing.Final = 3
EXTERNAL_CLIENT_TITLE_FOR_SCHEMA: typing.Final = "User/Client"
SERVICE_NODE_ID: typing.Final = "fastarch_service"
HELM_CHART_MARKER_FILE_NAME: typing.Final = "Chart.yaml"
HELM_CHART_SEARCH_DIRS: typing.Final = ("deploy", "helm", "charts", ".helm")
HELM_NESTED_LOOKUP_DEPTH: typing.Final = 4
# Ordered shallowest first so the search returns the top most chart and stops there,
# instead of walking an entire monorepo the way an unbounded rglob would.
HELM_NESTED_LOOKUP_PATTERNS: typing.Final = tuple(
    "/".join([*itertools.repeat("*", one_depth), HELM_CHART_MARKER_FILE_NAME])
    for one_depth in range(HELM_NESTED_LOOKUP_DEPTH)
)
HELM_CHART_LOOKUP_PATTERNS: typing.Final = HELM_NESTED_LOOKUP_PATTERNS[:2]
HELM_PARENT_LOOKUP_DEPTH: typing.Final = 3
HELM_MANIFEST_SEARCH_PATTERNS: typing.Final = (
    "Chart.yaml",
    "values.yaml",
    "values.yml",
    "templates/*.yaml",
    "templates/*.yml",
)
TYPICAL_RE_FLAGS: typing.Final = py_re.IGNORECASE | py_re.MULTILINE | py_re.UNICODE | py_re.DOTALL
DEFAULT_PATH: typing.Final = "/docs/architecture/"
DEFAULT_ROOT_DIR: typing.Final = pathlib.Path()
DEFAULT_SERVICE_NAME: typing.Final = "example-service"
UI_PLACEHOLDER_PATTER: typing.Final = py_re.compile(
    r"(?P<pre_open><pre[^>]*>)(?P<pre_body>.*?)(?P<pre_close></pre>)",
    flags=TYPICAL_RE_FLAGS,
)
# Collapsing whitespace runs keeps the page small, but the separator has to survive:
# joining with "" glues attributes together and yields `<script src=...>` as `<scriptsrc=...>`,
# which silently stops the browser from ever loading mermaid.
UI_HTML_TEMPLATE: typing.Final = " ".join(
    pathlib.Path(__file__).parent.joinpath("template.html").read_text().strip().split(),
)
