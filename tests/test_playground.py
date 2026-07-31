import typing

import pytest
from fastapi.testclient import TestClient

from tests.playground import INDEX_PATH, PLAYGROUND_EXAMPLES, playground_app, render_example_path


_GOOD_HTTP_CODE: typing.Final = 200


def test_index_links_every_example() -> None:
    response: typing.Final = TestClient(playground_app).get(INDEX_PATH)

    assert response.status_code == _GOOD_HTTP_CODE
    for one_example_name, one_example_settings in PLAYGROUND_EXAMPLES.items():
        assert f'href="/{one_example_name}/"' in response.text
        assert one_example_settings.service_name in response.text


@pytest.mark.parametrize("example_name", PLAYGROUND_EXAMPLES)
def test_example_page_serves_its_own_service(example_name: str) -> None:
    response: typing.Final = TestClient(playground_app).get(render_example_path(example_name))

    assert response.status_code == _GOOD_HTTP_CODE
    assert "graph TB" in response.text
    assert PLAYGROUND_EXAMPLES[example_name].service_name in response.text
