import pathlib
import re as py_re
import typing
from importlib import resources


FILES_SEARCH_PATTERN: typing.Final = "*.py"
# A virtual environment is somebody else's code: the sources of uvicorn, redis and celery
# themselves match the very patterns the service is scanned for, and land on the diagram as
# its architecture. The walk matches these names relative to the project root rather than to
# the filesystem root, otherwise a service living in a `build` directory would skip itself.
SKIPPED_DIR_NAMES: typing.Final = frozenset(
    (
        ".git",
        ".venv",
        ".tox",
        ".nox",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        ".eggs",
        "venv",
        "node_modules",
        "__pycache__",
        "site-packages",
        "build",
        "dist",
    ),
)
MAX_WORKERS: typing.Final = 10
LINE_INDENT: typing.Final = " " * 4
VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION: typing.Final = 3
EXTERNAL_CLIENT_TITLE_FOR_SCHEMA: typing.Final = "User/Client"
EXTERNAL_CLIENT_NODE_ID: typing.Final = "external_client"
EXTERNAL_API_TITLE_FOR_SCHEMA: typing.Final = "External API"
EXTERNAL_API_NODE_ID: typing.Final = "External_API"
FALLBACK_SERVICE_NODE_ID: typing.Final = "archdocs_service"
TYPICAL_RE_FLAGS: typing.Final = py_re.IGNORECASE | py_re.MULTILINE | py_re.UNICODE | py_re.DOTALL
DEFAULT_PATH: typing.Final = "/docs/architecture/"
DEFAULT_ROOT_DIR: typing.Final = pathlib.Path()
DEFAULT_SERVICE_NAME: typing.Final = "example-service"
UI_PLACEHOLDER_PATTERN: typing.Final = py_re.compile(
    r"(?P<pre_open><pre[^>]*>)(?P<pre_body>.*?)(?P<pre_close></pre>)",
    flags=TYPICAL_RE_FLAGS,
)
# The template is read through the package rather than through `__file__`: a wheel that shipped
# without it fails here, on import, and `scripts/check-package-contents.py` is what catches that
# before the wheel leaves the machine.
UI_HTML_TEMPLATE: typing.Final = " ".join(
    resources.files(__package__).joinpath("template.html").read_text(encoding="utf-8").split(),
)
