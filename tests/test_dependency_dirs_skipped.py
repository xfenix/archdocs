import pathlib
import typing

import pytest

from fastarch import settings
from fastarch.main import SettingsForFastarch
from tests.served_page import render_diagram


_OWN_SOURCE: typing.Final = """import redis


cache_client = redis.Redis(host="localhost")
"""
_VENDORED_SOURCE: typing.Final = """import celery
import uvicorn


app = celery.Celery(__name__)
"""
_EMPTY_KUBERNETES_DIR: typing.Final = "no-charts-here"


def _build_project(project_path: pathlib.Path, vendored_relative_path: str, /) -> pathlib.Path:
    (project_path / "service.py").write_text(_OWN_SOURCE)
    vendored_dir: typing.Final = project_path / vendored_relative_path
    vendored_dir.mkdir(parents=True)
    (vendored_dir / "vendored.py").write_text(_VENDORED_SOURCE)
    (project_path / _EMPTY_KUBERNETES_DIR).mkdir()
    return project_path


@pytest.mark.parametrize(
    "vendored_relative_path",
    [".venv/lib/python3.12/site-packages/celery", "venv/celery", "node_modules/celery", "build/lib/celery"],
)
def test_dependencies_stay_out_of_the_diagram(tmp_path: pathlib.Path, vendored_relative_path: str) -> None:
    rendered_diagram: typing.Final = render_diagram(
        SettingsForFastarch(
            root_dir=_build_project(tmp_path, vendored_relative_path),
            service_name="vendor-svc",
            kubernetes_dir=_EMPTY_KUBERNETES_DIR,
        ),
    )

    assert 'redisdb["redis"]' in rendered_diagram
    assert "celery" not in rendered_diagram
    assert "uvicorn" not in rendered_diagram


def test_project_inside_skipped_name_parsed(tmp_path: pathlib.Path) -> None:
    project_path: typing.Final = tmp_path / "build" / "dist" / "myservice"
    project_path.mkdir(parents=True)

    rendered_diagram: typing.Final = render_diagram(
        SettingsForFastarch(
            root_dir=_build_project(project_path, ".venv/celery"),
            service_name="nested-svc",
            kubernetes_dir=_EMPTY_KUBERNETES_DIR,
        ),
    )

    assert 'redisdb["redis"]' in rendered_diagram
    assert "celery" not in rendered_diagram


def test_skipped_names_cover_dependencies() -> None:
    assert ".venv" in settings.SKIPPED_DIR_NAMES
    assert "site-packages" in settings.SKIPPED_DIR_NAMES
