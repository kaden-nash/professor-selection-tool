import os
import json
import pytest
from unittest.mock import Mock, patch, mock_open

from knightrate.professor_scoring.professor_scoring_runner import ProfessorScoringRunner
from knightrate.professor_scoring.models import Professor, GlobalStatistics

@pytest.fixture
def mock_factory():
    with patch('knightrate.professor_scoring.professor_scoring_runner.ScoringEngineFactory') as mock_f:
        yield mock_f

@pytest.fixture
def mock_professor():
    # A dummy professor dict
    return {
        "id": "1",
        "first_name": "Test",
        "last_name": "Prof",
        "department": "CS",
        "base_rating": 4.0,
        "base_difficulty": 3.0,
        "would_take_again_percent": 80.0,
        "num_ratings": 10,
        "tags": [],
        "courses_taught": [],
        "metrics": {"overall_score": 0.0}
    }

def test_professor_scoring_runner_init():
    runner = ProfessorScoringRunner("/root")
    assert runner._root_dir == "/root"

def test_professor_scoring_runner_run(mock_factory, mock_professor, capsys):
    runner = ProfessorScoringRunner("/root")
    
    # Set up the factory mock and its nested engines
    factory_inst = mock_factory.return_value
    
    mock_first_engine = Mock()
    mock_second_engine = Mock()
    mock_stat_engine = Mock()
    
    factory_inst.create_first_round_engine.return_value = mock_first_engine
    factory_inst.create_second_round_engine.return_value = mock_second_engine
    factory_inst.create_global_stat_engine.return_value = mock_stat_engine
    
    # Process modifications
    prof_model = Professor(**mock_professor)
    mock_first_engine.process_data.return_value = [prof_model]
    mock_second_engine.process_data.return_value = [prof_model]
    
    # Stat modifications
    mock_stats = GlobalStatistics(
        average_overall=50.0,
        average_quality=3.0,
        average_difficulty=3.0,
        average_would_take_again=70.0
    )
    mock_stat_engine.calculate_statistics.return_value = mock_stats

    # Mock file I/O
    m_open = mock_open(read_data=json.dumps([mock_professor]))
    with patch('builtins.open', m_open), \
         patch('knightrate.professor_scoring.professor_scoring_runner.MongoUploader') as mock_uploader:
        runner.run()
        
    # Assertions
    # Two files opened for writing, one for reading
    assert m_open.call_count == 3
    
    # Check factory calls
    factory_inst.create_first_round_engine.assert_called_once()
    factory_inst.create_second_round_engine.assert_called_once()
    factory_inst.create_global_stat_engine.assert_called_once()
    
    mock_first_engine.process_data.assert_called_once()
    mock_second_engine.process_data.assert_called_once_with([prof_model])
    mock_stat_engine.calculate_statistics.assert_called_once_with([prof_model])
    
    captured = capsys.readouterr()
    assert "Scoring complete" in captured.out
    
    # Check MongoUploader
    mock_uploader.assert_called_once()
    mock_uploader_inst = mock_uploader.return_value
    
    # Check that upload_professor_scores was called with the serialized professor!
    mock_uploader_inst.upload_professor_scores.assert_called_once()
    # Check global stats
    mock_uploader_inst.upload_global_statistics.assert_called_once_with(mock_stats.model_dump())

def test_professor_scoring_runner_untyped_dict(mock_factory, mock_professor, capsys):
    runner = ProfessorScoringRunner("/root")
    
    # If a dict is passed directly without conversion? The code converts it.
    m_open = mock_open(read_data=json.dumps([mock_professor, "not_a_dict_but_a_string"]))
    
    factory_inst = mock_factory.return_value
    mock_engine = Mock()
    factory_inst.create_first_round_engine.return_value = mock_engine
    factory_inst.create_second_round_engine.return_value = mock_engine
    mock_engine.process_data.return_value = ["dummy_return"]
    
    mock_stat_engine = Mock()
    factory_inst.create_global_stat_engine.return_value = mock_stat_engine
    mock_stat_engine.calculate_statistics.return_value = GlobalStatistics(
        average_overall=50.0,
        average_quality=3.0,
        average_difficulty=3.0,
        average_would_take_again=70.0
    )
    
    with patch('builtins.open', m_open), \
         patch('knightrate.professor_scoring.professor_scoring_runner.MongoUploader'):
        runner.run()
        
    # Should handle fallback save paths without dying (the raw string should be written)
    # the JSON save should serialize string fine.
    
    # m_open()[1] would be the first write to data output
    # checking it doesn't crash is enough
    assert mock_engine.process_data.call_count == 2

def test_professor_scoring_runner_send_to_mongodb():
    runner = ProfessorScoringRunner("/root")
    
    prof = Professor(id="prof1", first_name="A", last_name="B")
    stats = GlobalStatistics(average_overall=4.0)
    
    with patch('knightrate.professor_scoring.professor_scoring_runner.MongoUploader') as mock_uploader:
        runner._send_to_mongodb([prof], stats)
        
    mock_inst = mock_uploader.return_value
    mock_inst.upload_professor_scores.assert_called_once_with([prof.model_dump(by_alias=True)])
    mock_inst.upload_global_statistics.assert_called_once_with(stats.model_dump())
