import pytest
from unittest.mock import Mock, patch
import signal
import os

from knightrate.rmp_scraping.rmp_scrape_runner import RmpScrapeRunner

@pytest.fixture
def mock_components():
    with patch('knightrate.rmp_scraping.rmp_scrape_runner.GraphQLClient') as mc, \
         patch('knightrate.rmp_scraping.rmp_scrape_runner.RateLimiter') as mr, \
         patch('knightrate.rmp_scraping.rmp_scrape_runner.DataStorage') as ms, \
         patch('knightrate.rmp_scraping.rmp_scrape_runner.Monitor') as mm, \
         patch('knightrate.rmp_scraping.rmp_scrape_runner.ScraperEngine') as me:
        
        yield {
            'client': mc,
            'limiter': mr,
            'storage': ms,
            'monitor': mm,
            'engine': me,
        }

@pytest.fixture
def mock_os_exit():
    with patch('knightrate.rmp_scraping.rmp_scrape_runner.os._exit') as mock_exit:
        yield mock_exit

@pytest.fixture
def mock_dotenv():
    with patch('knightrate.rmp_scraping.rmp_scrape_runner.load_dotenv') as mock_ld:
        yield mock_ld

def test_rmp_scrape_runner_init():
    runner = RmpScrapeRunner("/test", limit_professors=10, limit_reviews=5)
    assert runner._output_dir == "/test"
    assert runner._limit_professors == 10
    assert runner._limit_reviews == 5

def test_rmp_scrape_runner_run_success(mock_components, mock_dotenv, capsys):
    runner = RmpScrapeRunner("/test", 10, 5)
    
    mock_engine_inst = mock_components['engine'].return_value
    
    with patch('knightrate.rmp_scraping.rmp_scrape_runner.signal.signal') as mock_signal:
        runner.run()
        
    mock_dotenv.assert_called_once()
    
    mock_components['limiter'].assert_called_once_with(rate=5.0)
    mock_components['client'].assert_called_once_with(mock_components['limiter'].return_value)
    mock_components['storage'].assert_called_once_with(output_dir="/test")
    mock_components['monitor'].assert_called_once()
    
    mock_components['engine'].assert_called_once_with(
        mock_components['client'].return_value,
        mock_components['storage'].return_value,
        mock_components['monitor'].return_value,
        limit_professors=10,
        limit_reviews=5
    )
    
    mock_engine_inst.run.assert_called_once()
    mock_signal.assert_called_once()

def test_rmp_scrape_runner_run_exception(mock_components, mock_dotenv, mock_os_exit, capsys):
    runner = RmpScrapeRunner("/test")
    
    mock_engine_inst = mock_components['engine'].return_value
    mock_engine_inst.run.side_effect = Exception("Crash")
    # Must mock monitor to prevent AttributeError when runner catches exc
    mock_engine_inst.monitor = mock_components['monitor'].return_value
    
    with patch('knightrate.rmp_scraping.rmp_scrape_runner.signal.signal'):
        runner.run()
        
    mock_engine_inst.monitor.close.assert_called_once()
    mock_os_exit.assert_called_once_with(1)
    
    captured = capsys.readouterr()
    assert "An error occurred during scraping: Crash" in captured.out

def test_rmp_scrape_runner_signal_handler(mock_components, mock_os_exit, capsys):
    runner = RmpScrapeRunner("/test")
    
    # Extract handler
    real_signal = signal.signal
    registered_handler = None
    
    def fake_signal(sig, handler):
        nonlocal registered_handler
        registered_handler = handler
        
    with patch('knightrate.rmp_scraping.rmp_scrape_runner.signal.signal', side_effect=fake_signal):
        mock_engine_inst = mock_components['engine'].return_value
        runner.run()
        
    assert registered_handler is not None
    
    # Setup mock engine features
    mock_engine_inst.monitor = mock_components['monitor'].return_value
    mock_future = Mock()
    mock_engine_inst.futures = [mock_future]
    
    registered_handler(signal.SIGINT, None)
    
    assert mock_engine_inst._is_cancelled is True
    mock_future.cancel.assert_called_once()
    mock_engine_inst.monitor.close.assert_called_once()
    mock_os_exit.assert_called_once_with(1)
    
    captured = capsys.readouterr()
    assert "Scraping interrupted by user." in captured.out
