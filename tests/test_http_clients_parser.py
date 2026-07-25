import typing

from hypothesis import given  # type: ignore[import-untyped]
from hypothesis import strategies as st  # type: ignore[import-untyped]

from fastarch.features.http_clients.parser import find_http_client_features


HTTP_CLIENTS: typing.Final = ("httpx", "aiohttp", "requests", "niquests")
ASYNC_CLIENTS: typing.Final = ("httpx", "aiohttp")
SYNC_CLIENTS: typing.Final = ("requests", "niquests")


@given(st.sampled_from(HTTP_CLIENTS))
def test_http_client_detects_imports(http_client: str) -> None:
    import_variants: typing.Final = [
        f"import {http_client}\n",
        f"from {http_client} import Something\n",
        f"from {http_client}.client import Client\n",
    ]

    for one_source in import_variants:
        features = find_http_client_features(one_source)
        assert http_client in features.clients_used
        assert features.has_external_calls


@given(st.sampled_from(ASYNC_CLIENTS))
def test_http_client_detects_async_clients(http_client: str) -> None:
    async_patterns: typing.Final = {
        "httpx": (
            "import httpx\nasync with httpx.AsyncClient() as client:\n    await client.get('http://example.com')\n"
        ),
        "aiohttp": (
            "import aiohttp\nasync with aiohttp.ClientSession() as session:\n"
            "    await session.get('http://example.com')\n"
        ),
    }

    features: typing.Final = find_http_client_features(async_patterns[http_client])
    assert http_client in features.clients_used
    assert features.async_used
    assert features.has_external_calls


@given(st.sampled_from(SYNC_CLIENTS))
def test_http_client_detects_sync_clients(http_client: str) -> None:
    sync_patterns: typing.Final = {
        "requests": "import requests\nresponse = requests.get('http://example.com')\n",
        "niquests": "import niquests\nresponse = niquests.post('http://example.com', json={'key': 'value'})\n",
    }

    features: typing.Final = find_http_client_features(sync_patterns[http_client])
    assert http_client in features.clients_used
    assert not features.async_used
    assert features.has_external_calls


_MULTIPLE_CLIENTS_STRATEGY: typing.Final = st.lists(
    st.sampled_from(HTTP_CLIENTS),
    min_size=2,
    max_size=4,
    unique=True,
)


@given(_MULTIPLE_CLIENTS_STRATEGY)
def test_http_client_detects_multiple_clients(client_names: list[str]) -> None:
    features: typing.Final = find_http_client_features("\n".join(f"import {one_client}" for one_client in client_names))

    for one_client in client_names:
        assert one_client in features.clients_used
    assert features.has_external_calls


@given(st.text())
def test_http_client_handles_non_http_code(source_code: str) -> None:
    if not any(one_client in source_code for one_client in HTTP_CLIENTS):
        features: typing.Final = find_http_client_features(source_code)
        assert len(features.clients_used) == 0
        assert not features.has_external_calls


def _has_no_http_clients(source_text: str) -> bool:
    return not any(one_client in source_text for one_client in HTTP_CLIENTS)


_NON_HTTP_TEXT_STRATEGY: typing.Final = st.text().filter(_has_no_http_clients)
_EDGE_CASES_STRATEGY: typing.Final = st.one_of(st.just(""), _NON_HTTP_TEXT_STRATEGY)


@given(_EDGE_CASES_STRATEGY)
def test_http_client_edge_cases(source_code: str) -> None:
    features: typing.Final = find_http_client_features(source_code)
    assert len(features.clients_used) == 0
    assert not features.async_used
    assert not features.has_external_calls
