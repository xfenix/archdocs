import typing

from litestar import Litestar, get
from litestar.response import Response

from fastarch import settings
from fastarch.integrations.common import _create_architecture_engine, _generate_architecture_html
from fastarch.main import SettingsForFastarch


def add_architecture_doc_routes(
    litestar_app: Litestar,
    route_path: str = settings.DEFAULT_PATH,
    arch_settings: SettingsForFastarch | None = None,
) -> None:
    arch_engine: typing.Final = _create_architecture_engine(arch_settings)

    @get(route_path)
    async def _handle_litestar_arch_doc_route() -> Response:
        return Response(
            _generate_architecture_html(arch_engine),
            media_type="text/html",
        )

    litestar_app.register(_handle_litestar_arch_doc_route)
