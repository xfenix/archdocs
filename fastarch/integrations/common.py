import dataclasses
import re as py_re
import typing

from fastarch import settings
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


def _generate_architecture_html(arch_engine: ArchitectureParserAndRenderer) -> str:
    rendered_diagram: typing.Final = arch_engine.search_features_and_draw_them()

    def _inject_diagram(placeholder_match: py_re.Match[str]) -> str:
        opening_tag: typing.Final = placeholder_match.group(1)
        closing_tag: typing.Final = placeholder_match.group(3)
        return f"{opening_tag}graph LR\n{rendered_diagram}{closing_tag}"

    return settings.UI_PLACEHOLDER_PATTER.sub(_inject_diagram, settings.UI_HTML_TEMPLATE)


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
