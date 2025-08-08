from hypothesis import given
from hypothesis import strategies as st

from fastarch.features.http_api.parser import find_fastapi_and_litestar_features


IN_METHODS: tuple[str, ...] = ("post", "put", "patch", "delete")
OUT_METHODS: tuple[str, ...] = ("get", "head", "options", "trace")
ALL_METHODS: tuple[str, ...] = IN_METHODS + OUT_METHODS


@given(st.sampled_from(ALL_METHODS))
def test_http_api_parser_detects_methods(method: str) -> None:
    src = (
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        f"@router.{method}('/x')\n"
        "async def endpoint() -> None:\n"
        "    pass\n"
    )
    features = find_fastapi_and_litestar_features(src)
    if method in IN_METHODS:
        assert all(
            (
                method in features.in_methods,
                features.in_methods_existed,
                not features.out_methods_existed,
            ),
        )
    else:
        assert all(
            (
                method in features.out_methods,
                features.out_methods_existed,
                not features.in_methods_existed,
            ),
        )
