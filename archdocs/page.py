import html
import typing

from archdocs import mermaid_syntax, settings
from archdocs.main import ArchitectureParserAndRenderer


def render_mermaid_text(arch_engine: ArchitectureParserAndRenderer, /) -> str:
    return f"{mermaid_syntax.DIAGRAM_HEADER}\n{arch_engine.render_architecture_diagram()}\n"


def render_markdown_text(arch_engine: ArchitectureParserAndRenderer, /) -> str:
    return f"```mermaid\n{render_mermaid_text(arch_engine)}```\n"


def _fill_asset_links(arch_engine: ArchitectureParserAndRenderer, /) -> str:
    page_settings: typing.Final = arch_engine.local_settings
    font_tag: typing.Final = (
        settings.FONT_STYLESHEET_TAG.format(html.escape(page_settings.font_stylesheet_url))
        if page_settings.font_stylesheet_url
        else ""
    )
    return settings.UI_HTML_TEMPLATE.replace(
        settings.MERMAID_SCRIPT_TAG.format(html.escape(settings.DEFAULT_MERMAID_SCRIPT_URL)),
        settings.MERMAID_SCRIPT_TAG.format(html.escape(page_settings.mermaid_script_url)),
    ).replace(settings.FONT_STYLESHEET_TAG.format(html.escape(settings.DEFAULT_FONT_STYLESHEET_URL)), font_tag)


def render_architecture_page(arch_engine: ArchitectureParserAndRenderer, /) -> str:
    # In `<pre>` the diagram is text, so markup characters are escaped or the browser eats the labels.
    escaped_diagram: typing.Final = render_mermaid_text(arch_engine).replace("&", "&amp;").replace("<", "&lt;")
    return settings.UI_PLACEHOLDER_PATTERN.sub(
        lambda placeholder_match: (
            f"{placeholder_match.group('pre_open')}{escaped_diagram}{placeholder_match.group('pre_close')}"
        ),
        _fill_asset_links(arch_engine),
        count=1,
    )
