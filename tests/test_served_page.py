import dataclasses
import pathlib
import re as py_re
import typing

import hypothesis
import pytest
from hypothesis import strategies as st

from archdocs import settings
from tests import diagram_parts, factories, generated_project, served_page
from tests.diagram_rendering import build_generated_settings, build_named_settings


# Minifying the template by joining on "" used to glue attributes onto their tags, turning the
# mermaid script tag into `<scriptsrc=...>`: the served document is the only proof there is.
_SERVICE_NAME: typing.Final = "page-svc"
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
# The diagram travels to the browser as text inside a `<pre>`: an `&` or a `<` that arrives
# unescaped is read as markup, and mermaid is handed a document instead of a diagram.
_UNESCAPED_AMPERSAND_PATTERN: typing.Final = py_re.compile(r"&(?!amp;|lt;)")
_SERVICE_CONNECTIONS: typing.Final = factories.ServiceConnectionsFactory.build()
_CHART_BLUEPRINT: typing.Final = factories.ChartBlueprintFactory.build()
_SOURCES_DIR_NAME: typing.Final = "src"
_CHART_DIR_NAME: typing.Final = "chart"


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


# The page is what everybody with the link reads, and the sources it was built from are full of
# passwords: a dsn, a broker url, a value a chart keeps for a Secret.
@pytest.mark.parametrize(_RENDERER_ARGUMENT, served_page.ALL_PAGE_RENDERERS, ids=served_page.FRAMEWORK_IDS)
def test_credentials_never_reach_the_page(render_page: served_page.PageRenderer, tmp_path: pathlib.Path) -> None:
    source_dir: typing.Final = tmp_path / _SOURCES_DIR_NAME
    source_dir.mkdir()
    arch_settings: typing.Final = dataclasses.replace(
        build_generated_settings(source_dir, generated_project.ALL_TECHNOLOGIES, _SERVICE_CONNECTIONS),
        kubernetes_dir=generated_project.write_generated_chart(tmp_path / _CHART_DIR_NAME, _CHART_BLUEPRINT),
    )

    page_html: typing.Final = render_page(arch_settings, None)

    assert _SERVICE_CONNECTIONS.database_host in page_html
    assert "://***@" in page_html
    assert _SERVICE_CONNECTIONS.user_password not in page_html
    assert _CHART_BLUEPRINT.secret_value not in page_html


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


# A service name is somebody's string, and the diagram it lands in is markup by the time the
# browser sees it: whatever the name is made of, the page must stay a page around it.
@pytest.mark.parametrize(_RENDERER_ARGUMENT, served_page.ALL_PAGE_RENDERERS, ids=served_page.FRAMEWORK_IDS)
@hypothesis.settings(deadline=None, max_examples=_HYPOTHESIS_EXAMPLES)
@hypothesis.given(service_name=st.text(min_size=1))
def test_service_name_never_smuggles_markup(
    render_page: served_page.PageRenderer,
    service_name: str,
) -> None:
    diagram_block: typing.Final = diagram_parts.extract_diagram_block(
        render_page(build_named_settings(service_name), None),
    )

    assert diagram_block
    assert "<" not in diagram_block
    assert not _UNESCAPED_AMPERSAND_PATTERN.search(diagram_block)
