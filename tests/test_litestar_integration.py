import pathlib
import typing

import pytest
from litestar import Litestar
from litestar.testing import TestClient

from fastarch import settings
from fastarch.integrations.litestar import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


_GOOD_HTTP_CODE: typing.Final = 200
_CONTENT_TYPE_HTML: typing.Final = "text/html"
_ROOT_FOR_LITESTAR_EXAMPLE: typing.Final = pathlib.Path(__file__).parent / "litestar"


@pytest.fixture
def litestar_app_dynamic() -> Litestar:
    return Litestar()


@pytest.fixture
def litestar_app_from_folder(litestar_app_dynamic: Litestar) -> Litestar:
    add_architecture_doc_routes(
        litestar_app_dynamic,
        arch_settings=SettingsForFastarch(
            root_dir=_ROOT_FOR_LITESTAR_EXAMPLE,
            service_name="litestar-test-service",
        ),
    )
    return litestar_app_dynamic


def test_real_app_folder_features_detected(litestar_app_from_folder: Litestar) -> None:
    response: typing.Final = TestClient(litestar_app_from_folder).get(settings.DEFAULT_PATH)
    assert response.status_code == _GOOD_HTTP_CODE
    assert _CONTENT_TYPE_HTML in response.headers["content-type"]
    response_text: typing.Final = response.text
    assert "mermaid" in response_text
    assert "graph LR" in response_text
    assert "litestar-test-service" in response_text
    response_text_lower: typing.Final = response_text.lower()
    assert "get" in response_text_lower
    assert "post" in response_text_lower
    assert "postgresql" in response_text_lower or "asyncpg" in response_text_lower
    assert "redis" in response_text_lower or "cache" in response_text_lower


def test_dynamic_app_with_custom_path(litestar_app_dynamic: Litestar) -> None:
    custom_path: typing.Final = "/custom/architecture"
    add_architecture_doc_routes(
        litestar_app_dynamic,
        route_path=custom_path,
        arch_settings=SettingsForFastarch(
            root_dir=_ROOT_FOR_LITESTAR_EXAMPLE,
            service_name="test-custom-path",
        ),
    )
    assert TestClient(litestar_app_dynamic).get(custom_path).status_code == _GOOD_HTTP_CODE
