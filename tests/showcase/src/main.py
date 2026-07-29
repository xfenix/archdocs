"""Entry point of the showcase service."""

import typing

from fastapi import FastAPI

from tests.showcase.src.api.orders import orders_router


def create_app() -> FastAPI:
    """Create and configure the showcase application."""
    application = FastAPI(title="showcase-service")
    application.include_router(orders_router)
    return application


app: typing.Final = create_app()
