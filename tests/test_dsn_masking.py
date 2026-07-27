import pathlib
import typing

import pytest

from fastarch.features.sqlalchemy.const import SQLAlchemyFeatures
from fastarch.features.sqlalchemy.renderer import render_sqlalchemy_features
from fastarch.main import ArchitectureParserAndRenderer, SettingsForFastarch


# The sqlalchemy parser captures the whole quoted dsn, so anything it finds is drawn onto
# a page the application serves publicly. Userinfo must never survive that trip.
_TESTS_ROOT: typing.Final = pathlib.Path(__file__).parent
_DSN_WITH_USERINFO: typing.Final = (
    "postgresql+asyncpg://user:password@localhost:5432/db",
    "postgresql+asyncpg://sometoken@localhost:5432/db",
    "postgresql+asyncpg://user@localhost:5432/db",
    "postgresql+asyncpg://user:password@/db?host=host1,host2",
)


def _render_dsn(raw_database_type: str) -> str:
    return render_sqlalchemy_features(
        SQLAlchemyFeatures(
            async_used=True,
            pooling_used=False,
            multiple_hosts=False,
            database_type=raw_database_type,
        ),
    )


@pytest.mark.parametrize("raw_database_type", _DSN_WITH_USERINFO)
def test_userinfo_is_always_masked(raw_database_type: str) -> None:
    rendered_diagram: typing.Final = _render_dsn(raw_database_type)
    assert "://***@" in rendered_diagram
    assert "sometoken" not in rendered_diagram
    assert "user:password" not in rendered_diagram
    assert "://user@" not in rendered_diagram


def test_dsn_without_userinfo_is_untouched() -> None:
    assert "***" not in _render_dsn("sqlite+aiosqlite:///db")


def test_credentials_never_reach_diagram() -> None:
    rendered_diagram: typing.Final = ArchitectureParserAndRenderer(
        local_settings=SettingsForFastarch(root_dir=_TESTS_ROOT / "litestar", service_name="litestar-svc"),
    ).render_architecture_diagram()
    assert "user:password" not in rendered_diagram
    assert "://***@" in rendered_diagram
