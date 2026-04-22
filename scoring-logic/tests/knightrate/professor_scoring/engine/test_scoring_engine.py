import pytest
from knightrate.professor_scoring.engine.scoring_engine import ScoringEngine
from knightrate.professor_scoring.models import Professor, Scores

class MockStrategy:
    def __init__(self, metric_name, score):
        self.metric_name = metric_name
        self.score = score

    def analyze(self, professor: Professor) -> dict:
        return {self.metric_name: self.score}

class TestScoringEngine:
    def test_engine_initialization(self):
        engine = ScoringEngine()
        assert engine.strategies == []

    def test_register_strategy(self):
        engine = ScoringEngine()
        mock_strategy = MockStrategy("test", 1.0)
        engine.register_strategy(mock_strategy)
        assert len(engine.strategies) == 1
        assert engine.strategies[0] == mock_strategy


    def test_score_professor(self):
        engine = ScoringEngine()
        engine.register_strategy(MockStrategy("rawDifficultyScore", 5.0))
        engine.register_strategy(MockStrategy("ratingScore", 3.0))
        
        prof = Professor(firstName="Test Prof")
        scored_prof = engine._score_professor(prof)
        assert scored_prof.scores is not None
        assert scored_prof.scores.raw_difficulty_score == 5.0
        assert scored_prof.scores.rating_score == 3.0

    def test_process_data_with_professors(self):
        engine = ScoringEngine()
        engine.register_strategy(MockStrategy("rawDifficultyScore", 5.0))
        engine.register_strategy(MockStrategy("ratingScore", 3.0))
        
        data = [Professor(firstName="Prof 1"), Professor(firstName="Prof 2")]
        processed = engine.process_data(data)
        
        assert len(processed) == 2
        assert processed[0].scores.raw_difficulty_score == 5.0
        assert processed[1].scores.raw_difficulty_score == 5.0

    def test_process_data_with_mixed_types(self):
        engine = ScoringEngine()
        engine.register_strategy(MockStrategy("rawDifficultyScore", 5.0))
        
        data = [Professor(firstName="Prof 1"), "Not a dict", 123]
        processed = engine.process_data(data)
        
        assert len(processed) == 3
        assert isinstance(processed[0], Professor)
        assert processed[0].scores.raw_difficulty_score == 5.0
        assert processed[1] == "Not a dict"
        assert processed[2] == 123
        
    def test_score_professor_with_existing_scores(self):
        engine = ScoringEngine()
        engine.register_strategy(MockStrategy("ratingScore", 4.0))
        
        prof = Professor(firstName="Test Prof")
        prof.scores = Scores(raw_difficulty_score=3.5)
        
        scored_prof = engine._score_professor(prof)
        assert scored_prof.scores is not None
        assert scored_prof.scores.raw_difficulty_score == 3.5
        assert scored_prof.scores.rating_score == 4.0
