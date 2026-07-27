import pathlib
import typing

import hypothesis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from hypothesis import strategies as st

from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


ROOT_FOR_FASTAPI_EXAMPLE: typing.Final = pathlib.Path(__file__).parent / "fastapi"
STATUS_OK: typing.Final = 200


@hypothesis.settings(deadline=None)
@hypothesis.given(
    service_name=st.text(
        min_size=1,
        max_size=10,
        alphabet=st.characters(whitelist_categories=["Ll", "Lu"], whitelist_characters=["_", "-"]),
    ),
    route_value=st.text(
        min_size=1,
        max_size=10,
        alphabet=st.characters(whitelist_categories=["Ll", "Lu"], whitelist_characters=["_", "-"]),
    ),
)
def test_arch_route_handles_random_path_service(service_name: str, route_value: str) -> None:
    fastapi_app: typing.Final = FastAPI()
    add_architecture_doc_routes(
        fastapi_app,
        route_path=f"/{route_value}",
        arch_settings=SettingsForFastarch(root_dir=ROOT_FOR_FASTAPI_EXAMPLE, service_name=service_name),
    )
    response: typing.Final = TestClient(fastapi_app).get(f"/{route_value}")
    assert response.status_code == STATUS_OK
    assert service_name in response.text
