import typing

import fastapi

from fastarch.integrations.fastapi import add_architecture_doc_routes


def test_add_architecture_doc_routes() -> None:
    fastapi_app: typing.Final = fastapi.FastAPI()
    add_architecture_doc_routes(fastapi_app)
    assert fastapi_app.routes
