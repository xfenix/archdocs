import pathlib
import typing

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastarch import settings
from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


GOOD_HTTP_CODE: typing.Final = 200


@pytest.fixture
def fastapi_app() -> FastAPI:
    return FastAPI()


def test_add_architecture_doc_routes(fastapi_app: FastAPI) -> None:
    root_for_fastapi_example_src: typing.Final = pathlib.Path(__file__).parent / "fastapi"
    add_architecture_doc_routes(
        fastapi_app,
        arch_settings=SettingsForFastarch(root_dir=root_for_fastapi_example_src, service_name="kek"),
    )
    assert TestClient(fastapi_app).get(settings.DEFAULT_PATH).status_code == GOOD_HTTP_CODE
