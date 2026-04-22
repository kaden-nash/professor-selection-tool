import pytest
from knightrate.professor_scoring.strategies.combined_difficulty_scorer import DifficultyScorer
from knightrate.professor_scoring.models import Professor, Scores

class TestCombinedDifficultyScorer:
    def test_initialization(self):
        scorer = DifficultyScorer()
        assert scorer.metric_name == "difficulty"

    def test_analyze_difficulty(self):
        scorer = DifficultyScorer()
        prof = Professor()
        prof.scores = Scores(raw_difficulty_score=3.0, tag_friction_score=70.0)
        result = scorer.analyze(prof)
        assert result["difficulty"] == 54.0

    def test_analyze_no_scores(self):
        scorer = DifficultyScorer()
        prof = Professor()
        result = scorer.analyze(prof)
        assert result["difficulty"] == 0.0
