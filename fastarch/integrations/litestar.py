import dataclasses
import typing

from litestar import Litestar, get
from litestar.response import Response

from fastarch import settings
from fastarch.integrations.common import _create_architecture_engine, _generate_architecture_html
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


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
    route_path: str = settings.DEFAULT_PATH,
    arch_settings: SettingsForFastarch | None = None,
) -> None:
    arch_engine: typing.Final = _create_architecture_engine(arch_settings)
    arch_handler: typing.Final = _LitestarArchDocRoute(arch_engine=arch_engine)
    route_handler: typing.Final = get(route_path)(arch_handler)
    litestar_app.register(route_handler)
