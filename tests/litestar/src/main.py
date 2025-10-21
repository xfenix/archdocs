"""Main Litestar application for testing."""

import typing

from litestar import Litestar

from tests.litestar.src.routes.items import items_router
from tests.litestar.src.routes.users import users_router


def create_app() -> Litestar:
    """Create and configure Litestar application."""
    return Litestar(
        route_handlers=[users_router, items_router],
        debug=True,
    )


app: typing.Final = create_app()
