import pathlib
import typing

import pytest
from litestar import Litestar
from litestar.testing import TestClient

from fastarch import settings
from fastarch.integrations.litestar import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


GOOD_HTTP_CODE: typing.Final = 200


@pytest.fixture
def litestar_app() -> Litestar:
    return Litestar()


def test_add_architecture_doc_routes(litestar_app: Litestar) -> None:
    _root_for_litestar_example_src: typing.Final = pathlib.Path(__file__).parent / "fastapi"
    add_architecture_doc_routes(
        litestar_app,
        arch_settings=SettingsForFastarch(root_dir=_root_for_litestar_example_src, service_name="test"),
    )
    client_for_test: typing.Final = TestClient(litestar_app)
    assert client_for_test.get(settings.DEFAULT_PATH).status_code == GOOD_HTTP_CODE
