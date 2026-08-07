import typing

import pytest
from fastapi.testclient import TestClient

from tests import playground
from tests.served_page import GOOD_HTTP_CODE


def test_index_links_every_example() -> None:
    response: typing.Final = TestClient(playground.playground_app).get(playground.INDEX_PATH)

    assert response.status_code == GOOD_HTTP_CODE
    for one_example_name, one_example_settings in playground.PLAYGROUND_EXAMPLES.items():
        assert f'href="/{one_example_name}/"' in response.text
        assert one_example_settings.service_name in response.text


@pytest.mark.parametrize("example_name", playground.PLAYGROUND_EXAMPLES)
def test_example_page_serves_its_own_service(example_name: str) -> None:
    response: typing.Final = TestClient(playground.playground_app).get(playground.render_example_path(example_name))

    assert response.status_code == GOOD_HTTP_CODE
    assert "graph TB" in response.text
    assert playground.PLAYGROUND_EXAMPLES[example_name].service_name in response.text
