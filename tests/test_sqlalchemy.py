import pathlib
import typing

import hypothesis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from fastarch.features.sqlalchemy.parser import find_sqlalchemy_features
from fastarch.integrations.fastapi import add_architecture_doc_routes
from fastarch.main import SettingsForFastarch


DSN_LIST: typing.Final[tuple[str, ...]] = (
    "postgresql+psycopg2://user:password@localhost:5432/dbname",
    "postgresql+asyncpg://user:password@/dbname?host=host1:5432&host=host2:5432&host=host3:5432",
    (
        "postgresql+asyncpg://user:password@localhost:5432/dbname?pool_size=10&max_overflow=5&pool_timeout=30&"
        "pool_recycle=1800"
    ),
    "postgresql+asyncpg://user:password@/dbname?host=host1,host2,host3&target_session_attrs=read-write",
    "postgresql+asyncpg://user:password@/dbname?host=host1,host2,host3&target_session_attrs=read-only",
    "postgresql+psycopg2://user:password@/dbname?host=host1,host2,host3&target_session_attrs=any",
    "postgresql+asyncpg://user:password@localhost:5432/dbname",
)

# Avoid long and complex line in decorator by predefining the alphabet.
ALPHABET: typing.Final[SearchStrategy[str]] = st.characters(
    whitelist_categories=["Ll", "Lu"],
    whitelist_characters=["_", "-"],
)

STATUS_OK: typing.Final = 200


def _is_async_dsn(dsn: str) -> bool:
    return "+async" in dsn or "aiosqlite" in dsn or "+aiomysql" in dsn


@hypothesis.given(st.sampled_from(sorted(DSN_LIST)))
def test_find_sqlalchemy_dsn_variants(dsn: str) -> None:
    is_async = _is_async_dsn(dsn)
    engine_type = "create_async_engine" if is_async else "create_engine"
    import_line = (
        "from sqlalchemy.ext.asyncio import create_async_engine" if is_async else "from sqlalchemy import create_engine"
    )
    pool_clause = ", pool_size=10" if "pool_" in dsn else ""
    src = f"{import_line}\n{engine_type}('{dsn}'{pool_clause})\n"
    features = find_sqlalchemy_features(src)
    assert features.database_type == dsn
    assert features.async_used is is_async
    assert not features.pooling_used
    assert features.target_session_attrs == ""


@hypothesis.given(
    service_name=st.text(
        min_size=1,
        max_size=10,
        alphabet=ALPHABET,
    )
)
def test_sqlalchemy_features_rendered_via_fastapi(service_name: str) -> None:
    app = FastAPI()
    root_dir = pathlib.Path(__file__).parent / "fastapi"
    add_architecture_doc_routes(
        app,
        route_path="/",
        arch_settings=SettingsForFastarch(root_dir=root_dir, service_name=service_name),
    )
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == STATUS_OK
    assert "sqlite+aiosqlite" in response.text
    assert service_name in response.text
