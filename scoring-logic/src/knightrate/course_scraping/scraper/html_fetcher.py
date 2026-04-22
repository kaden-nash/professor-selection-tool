from playwright.sync_api import sync_playwright, Browser, BrowserContext

class HtmlFetcher:
    """Fetches HTML content from given URLs using Playwright."""

    def __init__(self):
        self._playwright = sync_playwright().start()
        self.browser: Browser = self._playwright.chromium.launch(headless=True)
        self.context: BrowserContext = self.browser.new_context()

    def fetch_html(self, url: str) -> str:
        """Loads a page and returns its HTML."""
        page = self.context.new_page()
        
        try:
            page.goto(url, wait_until="networkidle")
            html = page.content()
        finally:
            page.close()
            
        return html

    def close(self):
        """Closes the browser and playwright session."""
        self.browser.close()
        self._playwright.stop()
