import pathlib
import typing

from fastapi import FastAPI
from fastapi.testclient import TestClient
from hypothesis import given, strategies as st

from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


ROOT_FOR_FASTAPI_EXAMPLE: typing.Final = pathlib.Path(__file__).parent.parent


@given(
    service_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=["Ll", "Lu"], whitelist_characters=["_", "-"])),
    route=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=["Ll", "Lu"], whitelist_characters=["_", "-"]))
)
def test_architecture_route_handles_random_path_and_service(service_name: str, route: str) -> None:
    app = FastAPI()
    add_architecture_doc_routes(
        app,
        route_path="/" + route,
        arch_settings=SettingsForFastarch(root_dir=ROOT_FOR_FASTAPI_EXAMPLE, service_name=service_name),
    )
    client = TestClient(app)
    response = client.get("/" + route)
    assert response.status_code == 200
    assert service_name in response.text
