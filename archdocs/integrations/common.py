import typing

from archdocs import settings
from archdocs.main import ArchitectureParserAndRenderer, SettingsForArchdocs


def _generate_architecture_html(arch_engine: ArchitectureParserAndRenderer) -> str:
    rendered_diagram: typing.Final = (
        arch_engine.render_architecture_diagram().replace("&", "&amp;").replace("<", "&lt;")
    )
    placeholder_match: typing.Final = settings.UI_PLACEHOLDER_PATTERN.search(settings.UI_HTML_TEMPLATE)
    if placeholder_match is None:
        return settings.UI_HTML_TEMPLATE
    prefix_end: typing.Final = placeholder_match.start()
    suffix_start: typing.Final = placeholder_match.end()
    diagram_block: typing.Final = (
        f"{placeholder_match.group('pre_open')}{settings.DIAGRAM_HEADER}\n"
        f"{rendered_diagram}{placeholder_match.group('pre_close')}"
    )
    return settings.UI_HTML_TEMPLATE[:prefix_end] + diagram_block + settings.UI_HTML_TEMPLATE[suffix_start:]


def _create_architecture_engine(
    arch_settings: SettingsForArchdocs | None,
) -> ArchitectureParserAndRenderer:
    if arch_settings is None:
        arch_settings = SettingsForArchdocs(
            root_dir=settings.DEFAULT_ROOT_DIR,
            service_name=settings.DEFAULT_SERVICE_NAME,
        )
    return ArchitectureParserAndRenderer(local_settings=arch_settings)
