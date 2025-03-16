import typing
from re import py_re


SHIFT_LEFT: typing.Final = " " * 4
EXTERNAL_CLIENT_SCHEMA: typing.Final = "User/Client"
TYPICAL_RE_FLAGS: typing.Final = py_re.IGNORECASE | py_re.MULTILINE | py_re.UNICODE
DEFAULT_PATH: typing.Final = "/docs/architecture/"
UI_HTML_TEMPLATE: typing.Final = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Architecture docs</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js" async></script>
    </head>
    <body>
        <pre class="mermaid">{}</pre>
    </body>
    </html>
""".strip()
