import pathlib
import re as py_re
import typing

from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch
from tests.playground import PLAYGROUND_EXAMPLES


# Tests enter the package through `ArchitectureParserAndRenderer`: the walk over the sources,
# every parser, every renderer and the mermaid syntax sit behind that one call, so a diagram
# read back from here is the one an application serves. The page around it, with its tags and
# its escaping, is the subject of `test_served_page.py` alone.
TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
FASTAPI_ROOT: typing.Final = TESTS_ROOT / "fastapi"
LITESTAR_ROOT: typing.Final = TESTS_ROOT / "litestar"
KUBERNETES_VARIANTS_ROOT: typing.Final = TESTS_ROOT / "kubernetes_variants"
# Manifests are looked up a couple of directories above the sources and the fixture charts live
# right in `tests/`, so a test whose expectations are about the service name alone points
# `kubernetes_dir` at a name no directory here has.
WITHOUT_MANIFESTS: typing.Final = "there-are-no-manifests-here"
SOURCE_SERVICE_NAME: typing.Final = "app-svc"
# The examples come from the playground, so the pages looked at by eye and the diagrams
# asserted on are built from one set of settings.
SHOWCASE_SETTINGS: typing.Final = PLAYGROUND_EXAMPLES["showcase"]
ALL_EXAMPLE_SETTINGS: typing.Final = (
    *PLAYGROUND_EXAMPLES.values(),
    SettingsForFastarch(root_dir=TESTS_ROOT / "kubernetes_fixtures", service_name="kubernetes-svc"),
)
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


def render_diagram(arch_settings: SettingsForFastarch, /) -> str:
    return ArchitectureParserAndRenderer(local_settings=arch_settings).render_architecture_diagram()


def render_source_diagram(project_path: pathlib.Path, source_code: str, /) -> str:
    (project_path / "main.py").write_text(source_code)
    return render_diagram(
        SettingsForFastarch(
            root_dir=project_path,
            service_name=SOURCE_SERVICE_NAME,
            kubernetes_dir=WITHOUT_MANIFESTS,
        ),
    )


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
