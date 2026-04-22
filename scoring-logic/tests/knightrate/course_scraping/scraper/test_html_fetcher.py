import pytest
from unittest.mock import patch
from src.knightrate.course_scraping.scraper.html_fetcher import HtmlFetcher

@pytest.fixture
def fetcher():
    with patch('knightrate.course_scraping.scraper.html_fetcher.sync_playwright') as mock_sync_pw:
        mock_pw = mock_sync_pw.return_value.start.return_value
        mock_browser = mock_pw.chromium.launch.return_value
        mock_context = mock_browser.new_context.return_value
        
        fetcher_inst = HtmlFetcher()
        yield fetcher_inst, mock_context

def test_fetch_html_success(fetcher):
    fetcher_inst, mock_context = fetcher
    mock_page = mock_context.new_page.return_value
    mock_page.content.return_value = "<html>mock</html>"
    
    html = fetcher_inst.fetch_html("http://example.com")
    
    mock_context.new_page.assert_called_once()
    mock_page.goto.assert_called_once_with("http://example.com", wait_until="networkidle")
    mock_page.content.assert_called_once()
    mock_page.close.assert_called_once()
    assert html == "<html>mock</html>"

def test_fetch_html_closes_page_on_error(fetcher):
    fetcher_inst, mock_context = fetcher
    mock_page = mock_context.new_page.return_value
    mock_page.goto.side_effect = Exception("Network error")
    
    with pytest.raises(Exception):
        fetcher_inst.fetch_html("http://example.com")
        
    mock_page.close.assert_called_once()

def test_close_calls_browser_close(fetcher):
    fetcher_inst, _ = fetcher
    fetcher_inst.close()
    
    fetcher_inst.browser.close.assert_called_once()
    fetcher_inst._playwright.stop.assert_called_once()
