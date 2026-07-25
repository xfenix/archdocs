import dataclasses
import typing

from fastarch import settings
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


def _generate_architecture_html(arch_engine: ArchitectureParserAndRenderer) -> str:
    rendered_diagram: typing.Final = arch_engine.search_features_and_draw_them()
    placeholder_match: typing.Final = settings.UI_PLACEHOLDER_PATTER.search(settings.UI_HTML_TEMPLATE)
    if placeholder_match is None:
        return settings.UI_HTML_TEMPLATE
    diagram_block: typing.Final = (
        f"{placeholder_match.group('pre_open')}graph LR\n{rendered_diagram}{placeholder_match.group('pre_close')}"
    )
    return (
        settings.UI_HTML_TEMPLATE[: placeholder_match.start()]
        + diagram_block
        + settings.UI_HTML_TEMPLATE[placeholder_match.end() :]
    )


def _create_architecture_engine(
    arch_settings: SettingsForFastarch | None,
) -> ArchitectureParserAndRenderer:
    if arch_settings is None:
        arch_settings = SettingsForFastarch(
            root_dir=settings.DEFAULT_ROOT_DIR,
            service_name=settings.DEFAULT_SERVICE_NAME,
        )
    return ArchitectureParserAndRenderer(arch_settings)


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class ArchitectureRouteConfig:
    route_path: str
    arch_settings: SettingsForFastarch | None
