import typing

from hypothesis import given  # type: ignore[import-untyped]
from hypothesis import strategies as st  # type: ignore[import-untyped]

from fastarch.features.http_clients.parser import find_http_client_features


HTTP_CLIENTS: typing.Final = ("httpx", "aiohttp", "requests", "niquests")
ASYNC_CLIENTS: typing.Final = ("httpx", "aiohttp")
SYNC_CLIENTS: typing.Final = ("requests", "niquests")


@given(st.sampled_from(HTTP_CLIENTS))
def test_http_client_detects_imports(client: str) -> None:
    import_variants = [
        f"import {client}\n",
        f"from {client} import Something\n",
        f"from {client}.client import Client\n",
    ]

    for src in import_variants:
        features = find_http_client_features(src)
        assert client in features.clients_used
        assert features.has_external_calls


@given(st.sampled_from(ASYNC_CLIENTS))
def test_http_client_detects_async_clients(client: str) -> None:
    async_patterns = {
        "httpx": (
            "import httpx\nasync with httpx.AsyncClient() as client:\n    await client.get('http://example.com')\n"
        ),
        "aiohttp": (
            "import aiohttp\nasync with aiohttp.ClientSession() as session:\n"
            "    await session.get('http://example.com')\n"
        ),
    }

    src = async_patterns[client]
    features = find_http_client_features(src)
    assert client in features.clients_used
    assert features.async_used
    assert features.has_external_calls


@given(st.sampled_from(SYNC_CLIENTS))
def test_http_client_detects_sync_clients(client: str) -> None:
    sync_patterns = {
        "requests": "import requests\nresponse = requests.get('http://example.com')\n",
        "niquests": "import niquests\nresponse = niquests.post('http://example.com', json={'key': 'value'})\n",
    }

    src = sync_patterns[client]
    features = find_http_client_features(src)
    assert client in features.clients_used
    assert not features.async_used
    assert features.has_external_calls


_MULTIPLE_CLIENTS_STRATEGY = st.lists(
    st.sampled_from(HTTP_CLIENTS),
    min_size=2,
    max_size=4,
    unique=True,
)


@given(_MULTIPLE_CLIENTS_STRATEGY)
def test_http_client_detects_multiple_clients(clients: list[str]) -> None:
    src = "\n".join(f"import {client}" for client in clients)
    features = find_http_client_features(src)

    for client in clients:
        assert client in features.clients_used
    assert features.has_external_calls


@given(st.text())
def test_http_client_handles_non_http_code(src: str) -> None:
    if not any(client in src for client in HTTP_CLIENTS):
        features = find_http_client_features(src)
        assert len(features.clients_used) == 0
        assert not features.has_external_calls


def _has_no_http_clients(text: str) -> bool:
    return not any(client in text for client in HTTP_CLIENTS)


_NON_HTTP_TEXT_STRATEGY = st.text().filter(_has_no_http_clients)
_EDGE_CASES_STRATEGY = st.one_of(st.just(""), _NON_HTTP_TEXT_STRATEGY)


@given(_EDGE_CASES_STRATEGY)
def test_http_client_edge_cases(src: str) -> None:
    features = find_http_client_features(src)
    assert len(features.clients_used) == 0
    assert not features.async_used
    assert not features.has_external_calls
