import pathlib
import typing

from fastarch.integrations.common import _create_architecture_engine, _generate_architecture_html
from fastarch.main import SettingsForFastarch


def test_architecture_engine_default_settings() -> None:
    assert _create_architecture_engine(None) is not None


def test_architecture_engine_custom_settings() -> None:
    custom_settings: typing.Final = SettingsForFastarch(
        root_dir=pathlib.Path(__file__).parent,
        service_name="test-service",
    )
    arch_engine: typing.Final = _create_architecture_engine(custom_settings)
    assert arch_engine is not None
    assert arch_engine.local_settings.service_name == "test-service"


def test_generate_architecture_html() -> None:
    rendered_html: typing.Final = _generate_architecture_html(_create_architecture_engine(None))
    assert isinstance(rendered_html, str)
    assert len(rendered_html) > 0
