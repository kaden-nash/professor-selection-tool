import pytest
from unittest.mock import patch, MagicMock
from src.knightrate.prof_scraping.scraper.client import CatalogClient, UCF_CATALOG_URL, CONTENT_SELECTOR


class TestCatalogClientFetchHtml:
    """Tests for fetch_html using a fully mocked Playwright."""

    def _make_mock_playwright(self, html: str = "<html/>"):
        """Build a nested mock mimicking the playwright sync API."""
        mock_page = MagicMock()
        mock_page.content.return_value = html

        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_chromium = MagicMock()
        mock_chromium.launch.return_value = mock_browser

        mock_playwright = MagicMock()
        mock_playwright.__enter__ = MagicMock(return_value=mock_playwright)
        mock_playwright.__exit__ = MagicMock(return_value=False)
        mock_playwright.chromium = mock_chromium

        return mock_playwright, mock_browser, mock_page

    def test_fetch_html_returns_page_content(self):
        mock_pw, _, _ = self._make_mock_playwright("<html>test</html>")
        with patch("knightrate.prof_scraping.scraper.client.sync_playwright", return_value=mock_pw):
            result = CatalogClient().fetch_html()
        assert result == "<html>test</html>"

    def test_fetch_html_navigates_to_correct_url(self):
        mock_pw, _, mock_page = self._make_mock_playwright()
        with patch("knightrate.prof_scraping.scraper.client.sync_playwright", return_value=mock_pw):
            CatalogClient().fetch_html()
        args, _ = mock_page.goto.call_args
        assert args[0] == UCF_CATALOG_URL

    def test_fetch_html_waits_for_content_selector(self):
        mock_pw, _, mock_page = self._make_mock_playwright()
        with patch("knightrate.prof_scraping.scraper.client.sync_playwright", return_value=mock_pw):
            CatalogClient().fetch_html()
        args, _ = mock_page.wait_for_selector.call_args
        assert args[0] == CONTENT_SELECTOR

    def test_fetch_html_closes_browser_on_success(self):
        mock_pw, mock_browser, _ = self._make_mock_playwright()
        with patch("knightrate.prof_scraping.scraper.client.sync_playwright", return_value=mock_pw):
            CatalogClient().fetch_html()
        mock_browser.close.assert_called_once()

    def test_fetch_html_launches_headless(self):
        mock_pw, _, _ = self._make_mock_playwright()
        with patch("knightrate.prof_scraping.scraper.client.sync_playwright", return_value=mock_pw):
            CatalogClient().fetch_html()
        _, launch_kwargs = mock_pw.chromium.launch.call_args
        assert launch_kwargs.get("headless") is True
