import pathlib

from fastarch.integrations.common import _create_architecture_engine, _generate_architecture_html
from fastarch.main import SettingsForFastarch


def test_architecture_engine_default_settings() -> None:
    engine = _create_architecture_engine(None)
    assert engine is not None


def test_architecture_engine_custom_settings() -> None:
    custom_settings = SettingsForFastarch(
        root_dir=pathlib.Path(__file__).parent,
        service_name="test-service",
    )
    engine = _create_architecture_engine(custom_settings)
    assert engine is not None
    assert engine.local_settings.service_name == "test-service"


def test_generate_architecture_html() -> None:
    engine = _create_architecture_engine(None)
    html = _generate_architecture_html(engine)
    assert isinstance(html, str)
    assert len(html) > 0
