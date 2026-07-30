import typing

from hypothesis import given
from hypothesis import strategies as st

from fastarch.features.http_api.parser import find_fastapi_and_litestar_features


# A route is traffic the service receives whatever verb it answers, so the parser keeps one
# list: `get` used to be filed as an outgoing method and drawn as an arrow leaving the service.
ALL_METHODS: typing.Final[tuple[str, ...]] = ("post", "put", "patch", "delete", "get", "head", "options", "trace")


@given(st.sampled_from(ALL_METHODS))
def test_http_api_parser_detects_methods(http_method: str) -> None:
    source_code: typing.Final = (
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        f"@router.{http_method}('/x')\n"
        "async def endpoint() -> None:\n"
        "    pass\n"
    )
    features: typing.Final = find_fastapi_and_litestar_features(source_code)
    assert features.served_methods == frozenset((http_method,))
    assert features.served_methods_existed


def test_no_methods_without_a_framework() -> None:
    features: typing.Final = find_fastapi_and_litestar_features("@router.get('/x')\n")
    assert features.served_methods == frozenset()
    assert not features.served_methods_existed
