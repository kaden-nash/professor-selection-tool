import pytest
from unittest.mock import patch
from pathlib import Path

from src.knightrate.prof_scraping.prof_scrape_runner import ProfScrapeRunner

@pytest.fixture
def mock_components():
    with patch('src.knightrate.prof_scraping.prof_scrape_runner.CatalogClient') as mc, \
         patch('src.knightrate.prof_scraping.prof_scrape_runner.CatalogParser') as mp, \
         patch('src.knightrate.prof_scraping.prof_scrape_runner.DataStorage') as ms, \
         patch('src.knightrate.prof_scraping.prof_scrape_runner.ScraperEngine') as me:
        
        yield {
            'client': mc,
            'parser': mp,
            'storage': ms,
            'engine': me,
        }

@pytest.fixture
def mock_sys_exit():
    with patch('src.knightrate.prof_scraping.prof_scrape_runner.sys.exit') as mock_exit:
        yield mock_exit

def test_prof_scrape_runner_init():
    runner = ProfScrapeRunner(Path("/test"))
    assert runner._output_dir == Path("/test")

def test_prof_scrape_runner_run_success(mock_components):
    runner = ProfScrapeRunner(Path("/test"))
    
    mock_engine_inst = mock_components['engine'].return_value
    
    runner.run()
    
    mock_components['client'].assert_called_once()
    mock_components['parser'].assert_called_once()
    mock_components['storage'].assert_called_once_with(Path("/test"))
    mock_components['engine'].assert_called_once()
    
    mock_engine_inst.run.assert_called_once()

def test_prof_scrape_runner_run_exception(mock_components, capsys):
    runner = ProfScrapeRunner(Path("/test"))
    
    mock_engine_inst = mock_components['engine'].return_value
    mock_engine_inst.run.side_effect = Exception("Crash")
    
    with pytest.raises(Exception, match="Crash"):
        runner.run()
