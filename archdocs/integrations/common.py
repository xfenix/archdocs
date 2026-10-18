from archdocs import settings
from archdocs.main import ArchitectureParserAndRenderer, SettingsForArchdocs


def _create_architecture_engine(
    arch_settings: SettingsForArchdocs | None,
) -> ArchitectureParserAndRenderer:
    if arch_settings is None:
        arch_settings = SettingsForArchdocs(
            root_dir=settings.DEFAULT_ROOT_DIR,
            service_name=settings.DEFAULT_SERVICE_NAME,
        )
    return ArchitectureParserAndRenderer(local_settings=arch_settings)
