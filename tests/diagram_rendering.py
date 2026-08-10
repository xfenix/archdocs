import functools
import pathlib
import typing

from faker import Faker

from archdocs.main import ArchitectureParserAndRenderer, SettingsForArchdocs
from tests.playground import PLAYGROUND_EXAMPLES


# Faker only ever hands out lower-case words here, so the node id a random name collapses to is
# a plain hyphen-to-underscore swap — the same swap a test author would otherwise write by hand.
_RANDOM_NAME_GENERATOR: typing.Final = Faker()

SETTINGS_ARGUMENT: typing.Final = "arch_settings"
TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
FASTAPI_ROOT: typing.Final = TESTS_ROOT / "fastapi"
LITESTAR_ROOT: typing.Final = TESTS_ROOT / "litestar"
KUBERNETES_VARIANTS_ROOT: typing.Final = TESTS_ROOT / "kubernetes_variants"
# The lookup climbs out of any root inside `tests/` and reaches the fixture charts, so a bare
# service node is asked for by a directory name nothing here has.
WITHOUT_MANIFESTS: typing.Final = "there-are-no-manifests-here"
SOURCE_SERVICE_NAME: typing.Final = "app-svc"
SHOWCASE_SETTINGS: typing.Final = PLAYGROUND_EXAMPLES["showcase"]
ALL_EXAMPLE_SETTINGS: typing.Final = (
    *PLAYGROUND_EXAMPLES.values(),
    SettingsForArchdocs(root_dir=TESTS_ROOT / "kubernetes_fixtures", service_name="kubernetes-svc"),
)


def render_diagram(arch_settings: SettingsForArchdocs, /) -> str:
    return ArchitectureParserAndRenderer(local_settings=arch_settings).render_architecture_diagram()


# The examples are checked in and no test rewrites them, so the same settings give the same
# diagram all session long: layout, syntax and feature suites ask for them dozens of times.
@functools.cache
def render_example_diagram(arch_settings: SettingsForArchdocs, /) -> str:
    return render_diagram(arch_settings)


def build_named_settings(service_name: str, /) -> SettingsForArchdocs:
    return SettingsForArchdocs(
        root_dir=LITESTAR_ROOT,
        service_name=service_name,
        kubernetes_dir=WITHOUT_MANIFESTS,
    )


def generate_random_service_name() -> str:
    return f"{_RANDOM_NAME_GENERATOR.word()}-{_RANDOM_NAME_GENERATOR.word()}"


def build_expected_node_id(service_name: str, /) -> str:
    return service_name.replace("-", "_")


def render_source_diagram(project_path: pathlib.Path, source_code: str, /) -> str:
    (project_path / "main.py").write_text(source_code)
    return render_diagram(
        SettingsForArchdocs(
            root_dir=project_path,
            service_name=SOURCE_SERVICE_NAME,
            kubernetes_dir=WITHOUT_MANIFESTS,
        ),
    )
