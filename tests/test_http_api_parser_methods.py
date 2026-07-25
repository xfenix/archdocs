import typing

from hypothesis import given
from hypothesis import strategies as st

from fastarch.features.http_api.parser import find_fastapi_and_litestar_features


IN_METHODS: typing.Final[tuple[str, ...]] = ("post", "put", "patch", "delete")
OUT_METHODS: typing.Final[tuple[str, ...]] = ("get", "head", "options", "trace")
ALL_METHODS: typing.Final[tuple[str, ...]] = IN_METHODS + OUT_METHODS


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
    if http_method in IN_METHODS:
        assert all(
            (
                http_method in features.in_methods,
                features.in_methods_existed,
                not features.out_methods_existed,
            ),
        )
    else:
        assert all(
            (
                http_method in features.out_methods,
                features.out_methods_existed,
                not features.in_methods_existed,
            ),
        )
