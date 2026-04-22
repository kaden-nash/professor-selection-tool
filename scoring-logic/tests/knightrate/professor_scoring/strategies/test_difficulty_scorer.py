import pytest
from src.knightrate.professor_scoring.strategies.difficulty_scorer import RawDifficultyScorer
from src.knightrate.professor_scoring.models import Professor

class TestDifficultyScorer:
    def test_difficulty_scorer_initialization(self):
        scorer = RawDifficultyScorer()
        assert scorer.metric_name == "rawDifficultyScore"

    def test_extract_difficulty_valid(self):
        scorer = RawDifficultyScorer()
        prof = Professor(avg_difficulty=3.5)
        assert scorer._extract_difficulty(prof) == 3.5

    def test_extract_difficulty_missing(self):
        scorer = RawDifficultyScorer()
        prof = Professor()
        assert scorer._extract_difficulty(prof) == 0.0

    def test_extract_difficulty_string(self):
        scorer = RawDifficultyScorer()
        prof = Professor(avg_difficulty=4.2)
        assert scorer._extract_difficulty(prof) == 4.2

    def test_analyze_difficulty(self):
        scorer = RawDifficultyScorer()
        prof = Professor(avg_difficulty=3.8)
        result = scorer.analyze(prof)
        assert result == {"rawDifficultyScore": 3.8}

    def test_analyze_difficulty_missing(self):
        scorer = RawDifficultyScorer()
        prof = Professor()
        result = scorer.analyze(prof)
        assert result == {"rawDifficultyScore": 0.0}
