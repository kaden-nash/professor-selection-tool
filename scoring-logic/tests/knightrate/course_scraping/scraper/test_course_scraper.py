import pytest
from unittest.mock import MagicMock
from src.knightrate.course_scraping.scraper.course_scraper import CourseScraper

@pytest.fixture
def mocks():
    fetcher = MagicMock()
    parser = MagicMock()
    return fetcher, parser

def test_run_scraping_success(mocks):
    fetcher, parser = mocks
    
    fetcher.fetch_html.side_effect = ["<html>root</html>", "<html>group1</html>"]
    parser.extract_group_links.return_value = ["/group1"]
    parser.extract_course_titles.return_value = ["COURSE 1", "COURSE 2"]
    
    scraper = CourseScraper(fetcher, parser)
    courses = scraper.run_scraping("http://example.com")
    
    assert courses == ["COURSE 1", "COURSE 2"]
    assert fetcher.fetch_html.call_count == 2
    fetcher.fetch_html.assert_any_call("http://example.com/group1")
    parser.extract_group_links.assert_called_once_with("<html>root</html>")
    parser.extract_course_titles.assert_called_once_with("<html>group1</html>")

def test_run_scraping_skips_errors(mocks):
    fetcher, parser = mocks
    
    fetcher.fetch_html.side_effect = ["<html>root</html>", Exception("Timeout"), "<html>group2</html>"]
    parser.extract_group_links.return_value = ["/group1", "/group2"]
    parser.extract_course_titles.return_value = ["COURSE 3"]
    
    scraper = CourseScraper(fetcher, parser)
    courses = scraper.run_scraping("http://example.com")
    
    assert courses == ["COURSE 3"]
    assert fetcher.fetch_html.call_count == 3
