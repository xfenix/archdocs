import pathlib
import typing

from fastapi.testclient import TestClient as FastapiTestClient
from playwright.sync_api import sync_playwright

from tests.playground import playground_app, render_example_path


SCREENSHOT_TARGET_PATH: typing.Final = pathlib.Path("screenshot.png")
SCREENSHOT_EXAMPLE_NAME: typing.Final = "showcase"
# Ширина повторяет ту, под которую вставлен снимок в `README.md`: мермейд ужимает svg
# по ширине обёртки, так что от неё зависит масштаб диаграммы. Двойная плотность пикселей
# оставляет подписи узлов читаемыми после такого ужатия.
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
        browser: typing.Final = playwright_driver.chromium.launch()
        page: typing.Final = browser.new_page(
            viewport={"width": PAGE_WIDTH, "height": PAGE_HEIGHT_WHILE_RENDERING},
            device_scale_factor=PAGE_PIXEL_RATIO,
        )
        page.set_content(page_html)
        # Обёртка диаграммы прячется стилями и показывается из postRenderCallback мермейда,
        # так что её видимость — это и есть «диаграмма дорисована».
        page.wait_for_selector(DIAGRAM_SELECTOR, state="visible", timeout=DIAGRAM_RENDER_TIMEOUT_MS)
        page.evaluate("document.fonts.ready")
        # Снимается блок страницы, не окно: снимок целого окна не бывает короче него
        # самого и оставил бы под диаграммой полосу пустого фона.
        page.locator(PAGE_CONTENT_SELECTOR).screenshot(path=SCREENSHOT_TARGET_PATH)
        browser.close()


if __name__ == "__main__":
    take_screenshot_of_page(read_playground_page())
