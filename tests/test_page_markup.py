import typing

from fastarch import settings
from tests.served_page import extract_diagram, render_architecture_page


# Minifying the template by joining on "" used to glue attributes onto their tags, which
# turned the mermaid script tag into `<scriptsrc=...>` and stopped the diagram from ever
# loading in a browser. Nothing here reaches inside the package: the page a running
# application serves is the only thing that can prove the browser gets a working document.
_DEFAULT_NODE_OPENING: typing.Final = 'example_service{"'
_REQUIRED_PAGE_TAGS: typing.Final = (
    "<!DOCTYPE html>",
    '<html lang="en">',
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js">',
    '<pre class="archdoc__diagram">',
)


def test_page_keeps_every_required_tag() -> None:
    page_html: typing.Final = render_architecture_page()
    for one_required_tag in _REQUIRED_PAGE_TAGS:
        assert one_required_tag in page_html, one_required_tag


def test_omitted_settings_draw_the_default_name() -> None:
    rendered_diagram: typing.Final = extract_diagram(render_architecture_page())
    assert rendered_diagram.startswith(f"{settings.SHIFT_LEFT}{_DEFAULT_NODE_OPENING}")
    assert settings.DEFAULT_SERVICE_NAME in rendered_diagram
