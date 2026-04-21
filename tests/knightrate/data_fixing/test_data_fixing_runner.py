import pytest
from unittest.mock import patch

from knightrate.data_fixing.data_fixing_runner import DataFixingRunner

@pytest.fixture
def mock_course_scrub():
    with patch('knightrate.data_fixing.data_fixing_runner.CourseScrubber') as mock_cs:
        yield mock_cs

@pytest.fixture
def mock_rmp_scrub():
    with patch('knightrate.data_fixing.data_fixing_runner.RmpScrubber') as mock_rs:
        yield mock_rs

@pytest.fixture
def mock_catalog_scrub():
    with patch('knightrate.data_fixing.data_fixing_runner.CatalogScrubber') as mock_cts:
        yield mock_cts

@pytest.fixture
def mock_correlator():
    with patch('knightrate.data_fixing.data_fixing_runner.ProfessorCorrelator') as mock_pc:
        yield mock_pc

@pytest.fixture
def mock_os_path_exists():
    with patch('os.path.exists') as mock_exists:
        # Default to file existing
        mock_exists.return_value = True
        yield mock_exists

def test_data_fixing_runner_run_full(
    mock_course_scrub, mock_rmp_scrub, mock_catalog_scrub, mock_correlator, mock_os_path_exists, capsys
):
    runner = DataFixingRunner()
    
    cs_inst = mock_course_scrub.return_value
    cs_inst.get_data.return_value = ["course_data"]
    
    rs_inst = mock_rmp_scrub.return_value
    rs_inst.get_data.return_value = ["rmp_data"]
    
    cts_inst = mock_catalog_scrub.return_value
    cts_inst.get_data.return_value = ["catalog_data"]
    
    pc_inst = mock_correlator.return_value
    
    runner.run()
    
    # Assert
    assert mock_os_path_exists.call_count == 3
    
    cs_inst.load.assert_called_once()
    cs_inst.scrub.assert_called_once()
    cs_inst.save.assert_called_once()
    
    rs_inst.load.assert_called_once()
    rs_inst.scrub.assert_called_once()
    rs_inst.save.assert_called_once()
    
    cts_inst.load.assert_called_once()
    cts_inst.scrub.assert_called_once()
    cts_inst.save.assert_called_once()
    
    pc_inst.correlate.assert_called_once_with(["rmp_data"], ["catalog_data"], ["course_data"])
    pc_inst.save.assert_called_once()
    
def test_data_fixing_runner_missing_files(
    mock_course_scrub, mock_rmp_scrub, mock_catalog_scrub, mock_correlator, mock_os_path_exists, capsys
):
    runner = DataFixingRunner()
    # All files missing
    mock_os_path_exists.return_value = False
    
    runner.run()
    
    # Classes shouldn't be touched
    mock_course_scrub.assert_not_called()
    mock_rmp_scrub.assert_not_called()
    mock_catalog_scrub.assert_not_called()
    
    # Correlator won't run because required data is missing
    mock_correlator.assert_not_called()
    
    captured = capsys.readouterr()
    assert "skipping course scrub" in captured.out
    assert "skipping RMP scrub" in captured.out
    assert "skipping Catalog scrub" in captured.out
    assert "Missing data required for correlation, skipping." in captured.out
