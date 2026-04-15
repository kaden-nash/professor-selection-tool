import pytest
from unittest.mock import Mock, patch
import signal
import sys

from knightrate.prof_scraping.prof_scrape_runner import ProfScrapeRunner

@pytest.fixture
def mock_components():
    with patch('knightrate.prof_scraping.prof_scrape_runner.CatalogClient') as mc, \
         patch('knightrate.prof_scraping.prof_scrape_runner.CatalogParser') as mp, \
         patch('knightrate.prof_scraping.prof_scrape_runner.DataStorage') as ms, \
         patch('knightrate.prof_scraping.prof_scrape_runner.Monitor') as mm, \
         patch('knightrate.prof_scraping.prof_scrape_runner.ScraperEngine') as me:
        
        yield {
            'client': mc,
            'parser': mp,
            'storage': ms,
            'monitor': mm,
            'engine': me,
        }

@pytest.fixture
def mock_signal():
    with patch('knightrate.prof_scraping.prof_scrape_runner.signal.signal') as mock_sig:
        yield mock_sig
        
@pytest.fixture
def mock_sys_exit():
    with patch('knightrate.prof_scraping.prof_scrape_runner.sys.exit') as mock_exit:
        yield mock_exit

def test_prof_scrape_runner_init():
    runner = ProfScrapeRunner("/test")
    assert runner._output_dir == "/test"

def test_prof_scrape_runner_run_success(mock_components, mock_signal):
    runner = ProfScrapeRunner("/test")
    
    mock_engine_inst = mock_components['engine'].return_value
    mock_monitor_inst = mock_components['monitor'].return_value
    
    runner.run()
    
    mock_components['client'].assert_called_once()
    mock_components['parser'].assert_called_once()
    mock_components['storage'].assert_called_once_with("/test")
    mock_components['monitor'].assert_called_once()
    
    mock_components['engine'].assert_called_once()
    mock_signal.assert_called_once_with(signal.SIGINT, runner._setup_signal_handler.__code__.co_consts[1] if hasattr(runner._setup_signal_handler.__code__, 'co_consts') else mock.ANY) # can't easily assert nested func without ANY, but we can verify it registers
    
    mock_engine_inst.run.assert_called_once()

def test_prof_scrape_runner_run_exception(mock_components, mock_sys_exit, capsys):
    runner = ProfScrapeRunner("/test")
    
    mock_engine_inst = mock_components['engine'].return_value
    mock_monitor_inst = mock_components['monitor'].return_value
    
    mock_engine_inst.run.side_effect = Exception("Crash")
    
    runner.run()
    
    mock_monitor_inst.close.assert_called_once()
    mock_sys_exit.assert_called_once_with(1)
    
    captured = capsys.readouterr()
    assert "An error occurred: Crash" in captured.out

def test_prof_scrape_runner_signal_handler(mock_components, mock_sys_exit, capsys):
    runner = ProfScrapeRunner("/test")
    
    # We manually extract and trigger the signal handler to test it
    real_signal = signal.signal
    registered_handler = None
    
    def fake_signal(sig, handler):
        nonlocal registered_handler
        registered_handler = handler
        
    with patch('knightrate.prof_scraping.prof_scrape_runner.signal.signal', side_effect=fake_signal):
        # Prevent engine from actually running so we just test the handler registration
        mock_engine_inst = mock_components['engine'].return_value
        runner.run()
        
    assert registered_handler is not None
    
    # Trigger the handler
    mock_monitor_inst = mock_components['monitor'].return_value
    registered_handler(signal.SIGINT, None)
    
    mock_monitor_inst.close.assert_called_once()
    mock_sys_exit.assert_called_once_with(1)
    
    captured = capsys.readouterr()
    assert "Scrape interrupted by user." in captured.out
