import pytest
from unittest.mock import patch
from pathlib import Path

from knightrate.course_scraping.course_scrape_runner import CourseScrapeRunner, ROOT_URL

@pytest.fixture
def mock_fetcher():
    with patch('knightrate.course_scraping.course_scrape_runner.HtmlFetcher') as mock_f:
        yield mock_f

@pytest.fixture
def mock_parser():
    with patch('knightrate.course_scraping.course_scrape_runner.Parser') as mock_p:
        yield mock_p

@pytest.fixture
def mock_scraper():
    with patch('knightrate.course_scraping.course_scrape_runner.CourseScraper') as mock_s:
        yield mock_s

@pytest.fixture
def mock_storage():
    with patch('knightrate.course_scraping.course_scrape_runner.DataStorage') as mock_d:
        yield mock_d

def test_course_scrape_runner_init():
    runner = CourseScrapeRunner(Path("/test/dir"))
    assert runner._output_dir == Path("/test/dir")

def test_course_scrape_runner_run_success(mock_fetcher, mock_parser, mock_scraper, mock_storage, capsys):
    runner = CourseScrapeRunner(Path("/test/dir"))
    
    mock_fetcher_inst = mock_fetcher.return_value
    mock_scraper_inst = mock_scraper.return_value
    mock_storage_inst = mock_storage.return_value
    
    # Mock return value for scrape
    mock_courses = ["course1", "course2"]
    mock_scraper_inst.run_scraping.return_value = mock_courses
    
    runner.run()
    
    # Assertions
    mock_fetcher.assert_called_once()
    mock_scraper.assert_called_once_with(mock_fetcher_inst, mock_parser.return_value)
    mock_scraper_inst.run_scraping.assert_called_once_with(ROOT_URL)
    
    mock_storage.assert_called_once_with(Path("/test/dir"))
    mock_storage_inst.save_courses.assert_called_once_with(mock_courses)
    
    mock_fetcher_inst.close.assert_called_once()
    
    captured = capsys.readouterr()
    assert "Starting UCF Course Scraper" in captured.out
    assert "Successfully saved 2 courses." in captured.out

def test_course_scrape_runner_run_empty_results(mock_fetcher, mock_parser, mock_scraper, mock_storage, capsys):
    runner = CourseScrapeRunner(Path("/test/dir"))
    
    mock_fetcher_inst = mock_fetcher.return_value
    mock_scraper_inst = mock_scraper.return_value
    mock_storage_inst = mock_storage.return_value
    
    # Empty courses
    mock_scraper_inst.run_scraping.return_value = []
    
    runner.run()
    
    mock_storage_inst.save_courses.assert_not_called()
    mock_fetcher_inst.close.assert_called_once()
    
    captured = capsys.readouterr()
    assert "Finished scraping but no courses were found." in captured.out

def test_course_scrape_runner_run_exception(mock_fetcher, mock_scraper):
    runner = CourseScrapeRunner(Path("/test/dir"))
    mock_fetcher_inst = mock_fetcher.return_value
    mock_scraper_inst = mock_scraper.return_value
    
    mock_scraper_inst.run_scraping.side_effect = Exception("Scraping failed")
    
    with pytest.raises(Exception):
        runner.run()
        
    mock_fetcher_inst.close.assert_called_once()
