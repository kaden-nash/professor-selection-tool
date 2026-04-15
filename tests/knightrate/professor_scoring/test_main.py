import pytest
import json
import os
from unittest.mock import mock_open, patch, MagicMock
from knightrate.professor_scoring.main import main, load_data, save_data
from knightrate.professor_scoring.engine.engine_factory import ScoringEngineFactory
from knightrate.professor_scoring.models import Professor, Scores

class TestMain:
    @patch('builtins.open', new_callable=mock_open, read_data='[{"firstName": "Test"}]')
    def test_load_data(self, mock_file):
        result = load_data("fake_path.json")
        mock_file.assert_called_once()
        assert len(result) == 1
        assert isinstance(result[0], Professor)
        assert result[0].first_name == "Test"

    @patch('builtins.open', new_callable=mock_open)
    def test_save_data(self, mock_file):
        prof = Professor(firstName="Test")
        data = [prof]
        save_data("fake_path.json", data)
        mock_file.assert_called_once()
        handle = mock_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        assert '"firstName": "Test"' in written_content

    @patch('knightrate.professor_scoring.main.load_data')
    @patch('knightrate.professor_scoring.main.save_data')
    @patch('knightrate.professor_scoring.main.save_statistics')
    @patch('knightrate.professor_scoring.engine.engine_factory.ScoringEngineFactory.create_global_stat_engine')
    @patch('knightrate.professor_scoring.engine.engine_factory.ScoringEngineFactory.create_second_round_engine')
    @patch('knightrate.professor_scoring.engine.engine_factory.ScoringEngineFactory.create_first_round_engine')
    @patch('builtins.print')
    def test_main(self, mock_print, mock_create_first, mock_create_second, mock_create_global, mock_save_stats, mock_save_data, mock_load_data):
        prof = Professor(firstName="Test Prof")
        mock_load_data.return_value = [prof]
        
        scored_prof_1 = Professor(firstName="Test Prof")
        scored_prof_1.scores = Scores(difficulty_score=1.0)
        
        scored_prof_2 = Professor(firstName="Test Prof")
        scored_prof_2.scores = Scores(difficulty_score=1.0, rating_score=5.0)
        
        mock_engine_1 = MagicMock()
        mock_engine_1.process_data.return_value = [scored_prof_1]
        mock_create_first.return_value = mock_engine_1

        mock_engine_2 = MagicMock()
        mock_engine_2.process_data.return_value = [scored_prof_2]
        mock_create_second.return_value = mock_engine_2

        mock_engine_3 = MagicMock()
        mock_engine_3.calculate_statistics.return_value = "fake_stats"
        mock_create_global.return_value = mock_engine_3

        main()

        mock_load_data.assert_called_once()
        mock_create_first.assert_called_once()
        mock_engine_1.process_data.assert_called_once_with([prof])
        mock_create_second.assert_called_once()
        mock_engine_2.process_data.assert_called_once_with([scored_prof_1])
        mock_create_global.assert_called_once()
        mock_engine_3.calculate_statistics.assert_called_once_with([scored_prof_2])
        
        mock_save_data.assert_called_once_with("professor_ratings.json", [scored_prof_2])
        mock_save_stats.assert_called_once_with("global_statistics.json", "fake_stats")
        mock_print.assert_called_once_with("Scoring complete. Results saved to professor_ratings.json and global_statistics.json")
