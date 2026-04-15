from playwright.sync_api import sync_playwright, Page

UCF_CATALOG_URL = (
    "https://www.ucf.edu/catalog/undergraduate/"
    "#/content/66bcc88ef93938001c548385"
)
CONTENT_SELECTOR = "div.style__contentBody___gEuR0"
PAGE_LOAD_TIMEOUT_MS = 30_000


class CatalogClient:
    """Fetches rendered HTML from the UCF undergraduate catalog using Playwright."""

    def fetch_html(self) -> str:
        """Navigate to the catalog page and return fully-rendered HTML."""
        with sync_playwright() as playwright:
            browser = self._launch_browser(playwright)
            try:
                return self._load_page_html(browser)
            finally:
                browser.close()

    def _launch_browser(self, playwright):
        """Launch a headless Chromium instance."""
        return playwright.chromium.launch(headless=True)

    def _load_page_html(self, browser) -> str:
        """Open a new page, navigate to the catalog URL, and return its HTML."""
        page: Page = browser.new_page()
        page.goto(UCF_CATALOG_URL, timeout=PAGE_LOAD_TIMEOUT_MS)
        page.wait_for_selector(CONTENT_SELECTOR, timeout=PAGE_LOAD_TIMEOUT_MS)
        return page.content()
