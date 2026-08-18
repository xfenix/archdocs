import functools
import pathlib
import typing

from archdocs.main import ArchitectureParserAndRenderer, SettingsForArchdocs
from tests import factories, generated_project
from tests.playground import PLAYGROUND_EXAMPLES


SETTINGS_ARGUMENT: typing.Final = "arch_settings"
TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
FASTAPI_ROOT: typing.Final = TESTS_ROOT / "fastapi"
LITESTAR_ROOT: typing.Final = TESTS_ROOT / "litestar"
KUBERNETES_VARIANTS_ROOT: typing.Final = TESTS_ROOT / "kubernetes_variants"
KUBERNETES_FIXTURES_ROOT: typing.Final = TESTS_ROOT / "kubernetes_fixtures"
# The one service name written by hand: the feature table spells whole arrows, and the node id
# on both ends of them is what the name becomes.
SOURCE_SERVICE_NAME: typing.Final = "app-svc"
SHOWCASE_SETTINGS: typing.Final = PLAYGROUND_EXAMPLES["showcase"]
ALL_EXAMPLE_SETTINGS: typing.Final = (
    *PLAYGROUND_EXAMPLES.values(),
    SettingsForArchdocs(root_dir=KUBERNETES_FIXTURES_ROOT, service_name="kubernetes-svc"),
)


def render_diagram(arch_settings: SettingsForArchdocs, /) -> str:
    return ArchitectureParserAndRenderer(local_settings=arch_settings).render_architecture_diagram()


# The examples are checked in and no test rewrites them, so the same settings give the same
# diagram all session long: layout, syntax and feature suites ask for them dozens of times.
@functools.cache
def render_example_diagram(arch_settings: SettingsForArchdocs, /) -> str:
    return render_diagram(arch_settings)


def build_named_settings(service_name: str, /) -> SettingsForArchdocs:
    return factories.SettingsFactory.build(root_dir=LITESTAR_ROOT, service_name=service_name)


def render_source_diagram(project_path: pathlib.Path, source_code: str, /) -> str:
    (project_path / generated_project.SOURCE_FILE_NAME).write_text(source_code)
    return render_diagram(
        factories.SettingsFactory.build(root_dir=project_path, service_name=SOURCE_SERVICE_NAME),
    )


def render_generated_diagram(
    project_path: pathlib.Path,
    all_technologies: typing.Iterable[generated_project.OneTechnology],
    service_connections: factories.ServiceConnections,
    /,
) -> str:
    return render_diagram(build_generated_settings(project_path, all_technologies, service_connections))


def build_generated_settings(
    project_path: pathlib.Path,
    all_technologies: typing.Iterable[generated_project.OneTechnology],
    service_connections: factories.ServiceConnections,
    /,
) -> SettingsForArchdocs:
    generated_project.write_service_sources(project_path, all_technologies, service_connections)
    return factories.SettingsFactory.build(
        root_dir=project_path,
        service_name=service_connections.service_name,
    )
