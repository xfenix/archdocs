import re as py_re
import typing

from fastarch import settings


_DOUBLE_QUOTE: typing.Final = '"'
_UNSAFE_NODE_ID_PATTERN: typing.Final = py_re.compile(r"[^A-Za-z0-9_]+")


def render_node_id(raw_node_name: str) -> str:
    # Mermaid node ids reject `@`, `?` and `=`, which a dsn shaped name is full of.
    return _UNSAFE_NODE_ID_PATTERN.sub("_", raw_node_name).strip("_")


def render_edge_label(raw_label: str) -> str:
    # Mermaid fails to parse unquoted parentheses and commas inside edge labels,
    # so every label is wrapped in quotes and stripped of quotes of its own.
    return f'|"{raw_label.replace(_DOUBLE_QUOTE, "")}"|'


def render_edge(source_node: str, raw_label: str, target_node: str, /) -> str:
    # An empty label still has to disappear completely, `|""|` is a syntax error just
    # like the unquoted form is.
    if not raw_label:
        return f"{settings.SHIFT_LEFT}{source_node} --> {target_node}"
    return f"{settings.SHIFT_LEFT}{source_node} --> {render_edge_label(raw_label)} {target_node}"


def render_service_node_definition(service_name: str, node_annotations: typing.Iterable[str] = ()) -> str:
    # Mermaid requires an explicit node id, a bare `{name}` is a syntax error.
    joined_annotations: typing.Final = ", ".join(filter(None, node_annotations))
    safe_service_name: typing.Final = service_name.replace(_DOUBLE_QUOTE, "")
    if not joined_annotations:
        return f'{settings.SHIFT_LEFT}{settings.SERVICE_NODE_ID}{{"{safe_service_name}"}}'
    return f'{settings.SHIFT_LEFT}{settings.SERVICE_NODE_ID}{{"{safe_service_name} ({joined_annotations})"}}'
