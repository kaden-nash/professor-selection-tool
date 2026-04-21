import argparse
from unittest.mock import Mock, patch
import pytest

from run_pipeline import (
    PipelineConfig,
    StageResult,
    PipelineRunner,
    _parse_args,
    _build_config,
    main,
)
from knightrate.output_paths import RMP_SCRAPING_OUTPUT_DIR, COURSE_SCRAPING_OUTPUT_DIR, PROF_SCRAPING_OUTPUT_DIR

@pytest.fixture
def mock_runners():
    with patch('run_pipeline.RmpScrapeRunner') as mock_rmp, \
         patch('run_pipeline.ProfScrapeRunner') as mock_prof, \
         patch('run_pipeline.CourseScrapeRunner') as mock_course, \
         patch('run_pipeline.DataFixingRunner') as mock_df, \
         patch('run_pipeline.ProfessorScoringRunner') as mock_ps:
        yield {
            'rmp': mock_rmp,
            'prof': mock_prof,
            'course': mock_course,
            'data_fixing': mock_df,
            'scoring': mock_ps,
        }

def test_pipeline_config_defaults():
    config = PipelineConfig()
    assert not config.scrape_rmp
    assert not config.scrape_profs
    assert not config.scrape_courses
    assert not config.skip_fix
    assert not config.skip_scoring

def test_stage_result():
    result = StageResult(stage_name="Test Stage", success=True)
    assert result.stage_name == "Test Stage"
    assert result.success is True
    assert result.error is None

    result = StageResult(stage_name="Test Stage", success=False, error="Some error")
    assert result.success is False
    assert result.error == "Some error"

def test_pipeline_runner_run_default(mock_runners, capsys):
    config = PipelineConfig()
    runner = PipelineRunner(config)
    runner.run()
    
    # Optional stages shouldn't execute
    mock_runners['rmp'].assert_not_called()
    mock_runners['prof'].assert_not_called()
    mock_runners['course'].assert_not_called()
    
    # Required stages SHOULD execute
    mock_runners['data_fixing'].assert_called_once_with()
    mock_runners['scoring'].assert_called_once_with()
    
    assert len(runner._results) == 2
    assert runner._results[0].stage_name == "Data Fixing"
    assert runner._results[1].stage_name == "Professor Scoring"
    assert all(r.success for r in runner._results)
    
    # Check output
    captured = capsys.readouterr()
    assert "Stage: Data Fixing" in captured.out
    assert "Stage: Professor Scoring" in captured.out
    assert "PASS  Data Fixing" in captured.out
    assert "PASS  Professor Scoring" in captured.out

def test_pipeline_runner_optional_stages(mock_runners):
    config = PipelineConfig(
        scrape_rmp=True, 
        scrape_profs=True, 
        scrape_courses=True,
        skip_fix=True,
        skip_scoring=True
    )
    runner = PipelineRunner(config)
    runner.run()
    
    # Required stages skipped
    mock_runners['data_fixing'].assert_not_called()
    mock_runners['scoring'].assert_not_called()
    
    mock_runners['rmp'].assert_called_once_with(output_dir=RMP_SCRAPING_OUTPUT_DIR)
    mock_runners['prof'].assert_called_once_with(output_dir=PROF_SCRAPING_OUTPUT_DIR)
    mock_runners['course'].assert_called_once_with(output_dir=COURSE_SCRAPING_OUTPUT_DIR)
    
    assert len(runner._results) == 3
    assert runner._results[0].stage_name == "RMP Scraping"

def test_pipeline_runner_exception_handling(mock_runners):
    mock_df_instance = mock_runners['data_fixing'].return_value
    mock_df_instance.run.side_effect = ValueError("Mocked Failure")
    
    config = PipelineConfig(skip_scoring=True)
    runner = PipelineRunner(config)
    
    with patch('run_pipeline.traceback.format_exc', return_value="Mock Traceback"):
        runner.run()
        
    assert len(runner._results) == 1
    assert runner._results[0].success is False
    assert runner._results[0].error == "Mock Traceback"

def test_parse_args():
    with patch('argparse.ArgumentParser.parse_args') as mock_parse:
        mock_parse.return_value = argparse.Namespace(
            scrape_rmp=True,
            scrape_profs=False,
            scrape_courses=False,
            skip_fix=True,
            skip_scoring=False
        )
        args = _parse_args()
        assert args.scrape_rmp is True
        assert args.skip_fix is True
        assert args.skip_scoring is False

def test_build_config():
    args = argparse.Namespace(
        scrape_rmp=True,
        scrape_profs=False,
        scrape_courses=True,
        skip_fix=True,
        skip_scoring=False
    )
    config = _build_config(args)
    assert config.scrape_rmp is True
    assert config.scrape_profs is False
    assert config.scrape_courses is True
    assert config.skip_fix is True
    assert config.skip_scoring is False

def test_main():
    with patch('run_pipeline._parse_args') as mock_parse, \
         patch('run_pipeline._build_config') as mock_build, \
         patch('run_pipeline.PipelineRunner') as mock_runner_cls:
        
        mock_args = Mock()
        mock_parse.return_value = mock_args
        
        mock_config = Mock()
        mock_build.return_value = mock_config
        
        mock_runner_inst = mock_runner_cls.return_value
        
        main()
        
        mock_parse.assert_called_once()
        mock_build.assert_called_once_with(mock_args)
        mock_runner_cls.assert_called_once_with(mock_config)
        mock_runner_inst.run.assert_called_once()
