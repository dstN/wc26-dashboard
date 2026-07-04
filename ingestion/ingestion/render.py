import logging
from typing import Optional

import pandas as pd
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

_WAIT_SELECTOR = "table"
_TIMEOUT_MS = 30_000


async def render_tables(url: str) -> Optional[list[pd.DataFrame]]:
    """Playwright fallback for JS-rendered pages."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            page = await browser.new_page()
            await page.goto(url, timeout=_TIMEOUT_MS, wait_until="networkidle")
            await page.wait_for_selector(_WAIT_SELECTOR, timeout=_TIMEOUT_MS)
            html = await page.content()
        finally:
            await browser.close()

    try:
        tables = pd.read_html(html, flavor="lxml")
        logger.debug("render_tables: %d tables from %s", len(tables), url)
        return tables if tables else None
    except Exception as exc:
        logger.warning("render_tables parse failed for %s: %s", url, exc)
        return None
