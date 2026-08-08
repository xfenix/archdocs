import pathlib
import typing

from fastapi.testclient import TestClient as FastapiTestClient
from playwright.sync_api import sync_playwright

from tests.playground import playground_app, render_example_path


SCREENSHOT_TARGET_PATH: typing.Final = pathlib.Path("screenshot.png")
SCREENSHOT_EXAMPLE_NAME: typing.Final = "showcase"
# The width mirrors the one the screenshot is embedded with in `README.md`: mermaid shrinks
# the svg to the wrapper's width, so the diagram's scale depends on it. The doubled pixel
# density keeps the node labels readable after that shrinking.
PAGE_WIDTH: typing.Final = 900
PAGE_HEIGHT_WHILE_RENDERING: typing.Final = 800
PAGE_PIXEL_RATIO: typing.Final = 2
PAGE_CONTENT_SELECTOR: typing.Final = ".archdoc"
DIAGRAM_SELECTOR: typing.Final = ".archdoc__diagram-wrapper"
DIAGRAM_RENDER_TIMEOUT_MS: typing.Final = 60_000


def read_playground_page() -> str:
    playground_response: typing.Final = FastapiTestClient(playground_app).get(
        render_example_path(SCREENSHOT_EXAMPLE_NAME),
    )
    playground_response.raise_for_status()
    return playground_response.text


def take_screenshot_of_page(page_html: str, /) -> None:
    with sync_playwright() as playwright_driver:
        chromium_browser: typing.Final = playwright_driver.chromium.launch()
        showcase_page: typing.Final = chromium_browser.new_page(
            viewport={"width": PAGE_WIDTH, "height": PAGE_HEIGHT_WHILE_RENDERING},
            device_scale_factor=PAGE_PIXEL_RATIO,
        )
        showcase_page.set_content(page_html)
        # The diagram wrapper is hidden by styles and revealed from mermaid's postRenderCallback,
        # so its visibility is exactly "the diagram has finished rendering".
        showcase_page.wait_for_selector(DIAGRAM_SELECTOR, state="visible", timeout=DIAGRAM_RENDER_TIMEOUT_MS)
        showcase_page.evaluate("document.fonts.ready")
        # The page block is captured, not the window: a whole-window shot is never shorter than
        # the window itself and would leave a strip of empty background under the diagram.
        showcase_page.locator(PAGE_CONTENT_SELECTOR).screenshot(path=SCREENSHOT_TARGET_PATH)
        chromium_browser.close()


if __name__ == "__main__":
    take_screenshot_of_page(read_playground_page())
