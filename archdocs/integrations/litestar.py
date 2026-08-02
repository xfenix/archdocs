import dataclasses
import typing

from litestar import Litestar, get
from litestar.response import Response

from archdocs import settings
from archdocs.integrations.common import _create_architecture_engine, _generate_architecture_html
from archdocs.main import ArchitectureParserAndRenderer, SettingsForArchdocs


@typing.final
@dataclasses.dataclass(slots=True, frozen=True, kw_only=True)
class _LitestarArchDocRoute:
    arch_engine: ArchitectureParserAndRenderer

    async def __call__(self) -> Response[str]:
        return Response(
            _generate_architecture_html(self.arch_engine),
            media_type="text/html",
        )


def add_architecture_doc_routes(
    litestar_app: Litestar,
    *,
    route_path: str = settings.DEFAULT_PATH,
    arch_settings: SettingsForArchdocs | None = None,
) -> None:
    litestar_app.register(
        get(route_path)(
            _LitestarArchDocRoute(arch_engine=_create_architecture_engine(arch_settings)),
        ),
    )
