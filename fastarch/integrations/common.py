import re as py_re
import typing

from fastarch import settings
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


def _generate_architecture_html(arch_engine: ArchitectureParserAndRenderer) -> str:
    return py_re.sub(
        settings.UI_PLACEHOLDER_PATTER,
        arch_engine.search_features_and_draw_them(),
        settings.UI_HTML_TEMPLATE,
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
@typing.dataclass(slots=True, kw_only=True, frozen=True)
class ArchitectureRouteConfig:
    route_path: str
    arch_settings: SettingsForFastarch | None
