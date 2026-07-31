import typing

import hypothesis
import pytest
from hypothesis import strategies as st

from fastarch import settings
from fastarch.main import SettingsForFastarch
from tests.rendered_diagram import LITESTAR_ROOT, WITHOUT_MANIFESTS
from tests.served_page import ALL_PAGE_RENDERERS, FRAMEWORK_IDS, PageRenderer


# Minifying the template by joining on "" used to glue attributes onto their tags, turning the
# mermaid script tag into `<scriptsrc=...>`: the served document is the only proof there is.
_SERVICE_NAME: typing.Final = "page-svc"
_MARKED_UP_SERVICE_NAME: typing.Final = "svc<b>&x"
_RENDERER_ARGUMENT: typing.Final = "render_page"
_HYPOTHESIS_EXAMPLES: typing.Final = 20
_REQUIRED_PAGE_TAGS: typing.Final = (
    "<!DOCTYPE html>",
    '<html lang="en">',
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js">',
    '<pre class="archdoc__diagram">',
    settings.DIAGRAM_HEADER,
)
_NAME_ALPHABET: typing.Final = st.characters(whitelist_categories=["Ll", "Lu"], whitelist_characters=["_", "-"])
_NAME_STRATEGY: typing.Final = st.text(min_size=1, max_size=10, alphabet=_NAME_ALPHABET)


def _build_settings(service_name: str, /) -> SettingsForFastarch:
    return SettingsForFastarch(
        root_dir=LITESTAR_ROOT,
        service_name=service_name,
        kubernetes_dir=WITHOUT_MANIFESTS,
    )


@pytest.mark.parametrize(_RENDERER_ARGUMENT, ALL_PAGE_RENDERERS, ids=FRAMEWORK_IDS)
def test_default_route_serves_a_whole_document(render_page: PageRenderer) -> None:
    page_html: typing.Final = render_page(_build_settings(_SERVICE_NAME), None)

    for one_required_tag in _REQUIRED_PAGE_TAGS:
        assert one_required_tag in page_html, one_required_tag
    assert _SERVICE_NAME in page_html


@pytest.mark.parametrize(_RENDERER_ARGUMENT, ALL_PAGE_RENDERERS, ids=FRAMEWORK_IDS)
def test_omitted_settings_draw_the_default(render_page: PageRenderer) -> None:
    page_html: typing.Final = render_page(None, None)

    assert settings.DEFAULT_SERVICE_NAME in page_html
    assert 'example_service{"' in page_html


@pytest.mark.parametrize(_RENDERER_ARGUMENT, ALL_PAGE_RENDERERS, ids=FRAMEWORK_IDS)
def test_markup_characters_are_escaped(render_page: PageRenderer) -> None:
    page_html: typing.Final = render_page(_build_settings(_MARKED_UP_SERVICE_NAME), None)

    assert 'svc&lt;b>&amp;x"}' in page_html
    assert "svc<b>" not in page_html


@pytest.mark.parametrize(_RENDERER_ARGUMENT, ALL_PAGE_RENDERERS, ids=FRAMEWORK_IDS)
@hypothesis.settings(deadline=None, max_examples=_HYPOTHESIS_EXAMPLES)
@hypothesis.given(service_name=_NAME_STRATEGY, route_value=_NAME_STRATEGY)
def test_any_service_name_and_route_are_served(
    render_page: PageRenderer,
    service_name: str,
    route_value: str,
) -> None:
    page_html: typing.Final = render_page(_build_settings(service_name), f"/{route_value}")

    assert service_name in page_html
