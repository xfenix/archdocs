import pathlib
import typing

from fastarch import settings
from fastarch.integrations.common import _create_architecture_engine, _generate_architecture_html
from fastarch.main import SettingsForFastarch


# Minifying the template by joining on "" used to glue attributes onto their tags, which
# turned the mermaid script tag into `<scriptsrc=...>` and stopped the diagram from ever
# loading in a browser.
_REQUIRED_TEMPLATE_TAGS: typing.Final = (
    "<!DOCTYPE html>",
    '<html lang="en">',
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js">',
    '<pre class="archdoc__diagram">',
)


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


def test_template_tags_survive_minification() -> None:
    for one_required_tag in _REQUIRED_TEMPLATE_TAGS:
        assert one_required_tag in settings.UI_HTML_TEMPLATE, one_required_tag


def test_rendered_page_keeps_mermaid_script() -> None:
    rendered_html: typing.Final = _generate_architecture_html(_create_architecture_engine(None))
    assert "<script src=" in rendered_html
    assert "graph LR" in rendered_html
