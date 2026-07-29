import re as py_re
import typing

import pytest
from fastapi.testclient import TestClient

from tests.playground import INDEX_PATH, PLAYGROUND_EXAMPLES, playground_app, render_example_path
from tests.served_page import GOOD_HTTP_CODE, extract_diagram


# The playground is the only place where every supported technology is shown at once, so the
# example applications are held to that: whatever the package can detect has to be visible on
# one of the served pages, otherwise a capability is shipped with nothing to look at.
_REQUIRED_DIAGRAM_MARKS: typing.Final = (
    "REST",
    "httpx",
    "aiohttp",
    "requests",
    "niquests",
    "celery",
    "taskiq",
    "arq",
    "rq",
    "dramatiq",
    "huey",
    "rabbit",
    "kafka",
    "nats",
    "redis",
    "retry",
    "sentinel",
    "cluster",
    "postgresql",
    "sqlite",
    "replicas",
    "HPA",
)


def _render_every_diagram() -> str:
    playground_client: typing.Final = TestClient(playground_app)
    return "\n".join(
        extract_diagram(playground_client.get(render_example_path(one_example_name)).text)
        for one_example_name in PLAYGROUND_EXAMPLES
    )


def test_index_links_every_example() -> None:
    response: typing.Final = TestClient(playground_app).get(INDEX_PATH)
    assert response.status_code == GOOD_HTTP_CODE
    for one_example_name, one_example_settings in PLAYGROUND_EXAMPLES.items():
        assert f'href="/{one_example_name}/"' in response.text
        assert one_example_settings.service_name in response.text


@pytest.mark.parametrize("example_name", PLAYGROUND_EXAMPLES)
def test_example_page_serves_its_own_service(example_name: str) -> None:
    response: typing.Final = TestClient(playground_app).get(render_example_path(example_name))
    assert response.status_code == GOOD_HTTP_CODE
    assert "graph LR" in response.text
    assert PLAYGROUND_EXAMPLES[example_name].service_name in response.text


@pytest.mark.parametrize("feature_mark", _REQUIRED_DIAGRAM_MARKS)
def test_examples_show_every_supported_feature(feature_mark: str) -> None:
    assert py_re.search(rf"\b{feature_mark}\b", _render_every_diagram())
