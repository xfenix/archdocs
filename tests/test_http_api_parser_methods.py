from hypothesis import given
from hypothesis import strategies as st

from fastarch.features.http_api.parser import find_fastapi_and_litestar_features


IN_METHODS = ["post", "put", "patch", "delete"]
OUT_METHODS = ["get", "head", "options", "trace"]
ALL_METHODS = IN_METHODS + OUT_METHODS


@given(st.sampled_from(ALL_METHODS))
def test_find_fastapi_and_litestar_features_detects_methods(method: str) -> None:
    src = (
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        f"@router.{method}('/x')\n"
        "async def endpoint() -> None:\n"
        "    pass\n"
    )
    features = find_fastapi_and_litestar_features(src)
    if method in IN_METHODS:
        assert method in features.in_methods
        assert features.in_methods_existed
        assert not features.out_methods_existed
    else:
        assert method in features.out_methods
        assert features.out_methods_existed
        assert not features.in_methods_existed
