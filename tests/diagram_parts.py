import re as py_re
import typing


EDGE_ARROW: typing.Final = " --> "
_GROUP_BLOCK_PATTERN: typing.Final = py_re.compile(
    r'subgraph group_\w+\["(?P<group_title>[^"]+)"\]\n(?P<group_body>.*?)\n\s*end',
    flags=py_re.DOTALL,
)
_DEFINED_NODE_PATTERN: typing.Final = py_re.compile(r'(?m)^\s*(?P<node_id>[A-Za-z0-9_]+)\["')
_EDGE_ENDS_PATTERN: typing.Final = py_re.compile(r"(?m)^\s*(?P<source>\w+) -->.* (?P<target>\w+)$")


@typing.final
class EdgeEnds(typing.NamedTuple):
    source_id: str
    target_id: str


def extract_edge_lines(rendered_diagram: str, /) -> list[str]:
    return [one_line.strip() for one_line in rendered_diagram.split("\n") if EDGE_ARROW in one_line]


def collect_group_of_every_node(rendered_diagram: str, /) -> dict[str, str]:
    return {
        one_node_match.group("node_id"): one_group_match.group("group_title")
        for one_group_match in _GROUP_BLOCK_PATTERN.finditer(rendered_diagram)
        for one_node_match in _DEFINED_NODE_PATTERN.finditer(one_group_match.group("group_body"))
    }


def collect_defined_node_ids(rendered_diagram: str, /) -> list[str]:
    return [one_match.group("node_id") for one_match in _DEFINED_NODE_PATTERN.finditer(rendered_diagram)]


def collect_edge_ends(rendered_diagram: str, /) -> tuple[EdgeEnds, ...]:
    return tuple(
        EdgeEnds(source_id=one_match.group("source"), target_id=one_match.group("target"))
        for one_match in _EDGE_ENDS_PATTERN.finditer(rendered_diagram)
    )
