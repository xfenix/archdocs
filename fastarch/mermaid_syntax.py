import re as py_re
import typing

from fastarch import settings


_DOUBLE_QUOTE: typing.Final = '"'
_UNSAFE_NODE_ID_PATTERN: typing.Final = py_re.compile(r"[^A-Za-z0-9_]+")
_PLAIN_NODE_TEMPLATE: typing.Final = '{defined_node_id}["{node_label}"]'
_SERVICE_NODE_TEMPLATE: typing.Final = '{defined_node_id}{{"{node_label}"}}'


def render_node_id(raw_node_name: str) -> str:
    return _UNSAFE_NODE_ID_PATTERN.sub("_", raw_node_name).strip("_")


def render_service_node_id(service_name: str) -> str:
    return render_node_id(service_name) or settings.FALLBACK_SERVICE_NODE_ID


def render_edge_label(raw_label: str) -> str:
    return f'|"{raw_label.replace(_DOUBLE_QUOTE, "")}"|'


def render_edge(source_node: str, raw_label: str, target_node: str, /) -> str:
    edge_beginning: typing.Final = f"{settings.SHIFT_LEFT}{source_node} -->"
    if not raw_label:
        return f"{edge_beginning} {target_node}"
    return f"{edge_beginning} {render_edge_label(raw_label)} {target_node}"


def _render_node(defined_node_id: str, raw_node_label: str, node_template: str, /) -> str:
    return settings.SHIFT_LEFT + node_template.format(
        defined_node_id=defined_node_id,
        node_label=raw_node_label.replace(_DOUBLE_QUOTE, ""),
    )


def render_node_definition(defined_node_id: str, raw_node_label: str, /) -> str:
    return _render_node(defined_node_id, raw_node_label, _PLAIN_NODE_TEMPLATE)


def render_service_node_definition(service_name: str, node_annotations: typing.Iterable[str] = ()) -> str:
    joined_annotations: typing.Final = ", ".join(filter(None, node_annotations))
    return _render_node(
        render_service_node_id(service_name),
        f"{service_name} ({joined_annotations})" if joined_annotations else service_name,
        _SERVICE_NODE_TEMPLATE,
    )
