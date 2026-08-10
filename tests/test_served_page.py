import typing

import hypothesis
import pytest
from hypothesis import strategies as st

from archdocs import settings
from tests import diagram_rendering, served_page
from tests.diagram_rendering import build_named_settings


# Minifying the template by joining on "" used to glue attributes onto their tags, turning the
# mermaid script tag into `<scriptsrc=...>`: the served document is the only proof there is.
_SERVICE_NAME: typing.Final = diagram_rendering.generate_random_service_name()
_MARKED_UP_SERVICE_NAME: typing.Final = "svc<b>&x"
_RENDERER_ARGUMENT: typing.Final = "render_page"
_HYPOTHESIS_EXAMPLES: typing.Final = 20
_TEMPLATE_WITHOUT_A_SLOT: typing.Final = "<!DOCTYPE html><html lang='en'><body>no room here</body></html>"
_REQUIRED_PAGE_TAGS: typing.Final = (
    "<!DOCTYPE html>",
    '<html lang="en">',
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js">',
    '<pre class="archdoc__diagram">',
    "graph TB",
)
_NAME_ALPHABET: typing.Final = st.characters(whitelist_categories=["Ll", "Lu"], whitelist_characters=["_", "-"])
_NAME_STRATEGY: typing.Final = st.text(min_size=1, max_size=10, alphabet=_NAME_ALPHABET)


@pytest.mark.parametrize(_RENDERER_ARGUMENT, served_page.ALL_PAGE_RENDERERS, ids=served_page.FRAMEWORK_IDS)
def test_default_route_serves_a_whole_document(render_page: served_page.PageRenderer) -> None:
    page_html: typing.Final = render_page(build_named_settings(_SERVICE_NAME), None)

    for one_required_tag in _REQUIRED_PAGE_TAGS:
        assert one_required_tag in page_html, one_required_tag
    assert _SERVICE_NAME in page_html


# Without settings the scan starts from the working directory, which under pytest is the
# repository itself: the page has to name the default service and draw its node.
@pytest.mark.parametrize(_RENDERER_ARGUMENT, served_page.ALL_PAGE_RENDERERS, ids=served_page.FRAMEWORK_IDS)
def test_omitted_settings_draw_the_default(render_page: served_page.PageRenderer) -> None:
    page_html: typing.Final = render_page(None, None)

    assert 'example_service{"example-service' in page_html


# A template shipped without a `<pre>` slot has nowhere to put the diagram: the page still has
# to be a page.
@pytest.mark.parametrize(_RENDERER_ARGUMENT, served_page.ALL_PAGE_RENDERERS, ids=served_page.FRAMEWORK_IDS)
def test_template_without_a_slot_is_served_whole(
    render_page: served_page.PageRenderer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "UI_HTML_TEMPLATE", _TEMPLATE_WITHOUT_A_SLOT)

    page_html: typing.Final = render_page(build_named_settings(_SERVICE_NAME), None)

    assert page_html == _TEMPLATE_WITHOUT_A_SLOT


@pytest.mark.parametrize(_RENDERER_ARGUMENT, served_page.ALL_PAGE_RENDERERS, ids=served_page.FRAMEWORK_IDS)
def test_markup_characters_are_escaped(render_page: served_page.PageRenderer) -> None:
    page_html: typing.Final = render_page(build_named_settings(_MARKED_UP_SERVICE_NAME), None)

    assert 'svc&lt;b>&amp;x"}' in page_html
    assert "svc<b>" not in page_html


@pytest.mark.parametrize(_RENDERER_ARGUMENT, served_page.ALL_PAGE_RENDERERS, ids=served_page.FRAMEWORK_IDS)
@hypothesis.settings(deadline=None, max_examples=_HYPOTHESIS_EXAMPLES)
@hypothesis.given(service_name=_NAME_STRATEGY, route_value=_NAME_STRATEGY)
def test_any_service_name_and_route_are_served(
    render_page: served_page.PageRenderer,
    service_name: str,
    route_value: str,
) -> None:
    page_html: typing.Final = render_page(build_named_settings(service_name), f"/{route_value}")

    assert service_name in page_html
