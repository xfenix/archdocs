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
    _root_for_fastapi_example_src: typing.Final = pathlib.Path(__file__).parent.parent
    add_architecture_doc_routes(
        fastapi_app,
        arch_settings=SettingsForFastarch(root_dir=_root_for_fastapi_example_src, service_name="kek"),
    )
    client_for_test: typing.Final = TestClient(fastapi_app)
    assert client_for_test.get(settings.DEFAULT_PATH).status_code == GOOD_HTTP_CODE
