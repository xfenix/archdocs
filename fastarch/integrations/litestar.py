import functools
import typing

import litestar
from litestar import Litestar
from litestar.response import Response

from fastarch import settings
from fastarch.integrations.common import _create_architecture_engine, _generate_architecture_html
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


async def _handle_litestar_arch_doc_route(
    arch_engine: ArchitectureParserAndRenderer,
) -> Response:
    return Response(
        _generate_architecture_html(arch_engine),
        media_type="text/html",
    )


def _build_litestar_arch_doc_route(
    arch_engine: ArchitectureParserAndRenderer,
) -> typing.Callable[[], typing.Awaitable[Response]]:
    return functools.partial(_handle_litestar_arch_doc_route, arch_engine=arch_engine)


def add_architecture_doc_routes(
    litestar_app: Litestar,
    route_path: str = settings.DEFAULT_PATH,
    arch_settings: SettingsForFastarch | None = None,
) -> None:
    arch_engine: typing.Final = _create_architecture_engine(arch_settings)
    route_handler: typing.Final = _build_litestar_arch_doc_route(arch_engine)

    litestar_app.add_route_handler(
        litestar.get(route_path)(route_handler),
    )
