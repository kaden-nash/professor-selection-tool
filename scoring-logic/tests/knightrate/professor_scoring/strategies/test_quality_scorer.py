import pytest
from src.knightrate.professor_scoring.strategies.quality_scorer import QualityScorer
from src.knightrate.professor_scoring.models import Professor, Scores

class TestQualityScorer:
    def test_initialization(self):
        scorer = QualityScorer()
        assert scorer.metric_name == "quality"

    def test_analyze_quality(self):
        scorer = QualityScorer()
        prof = Professor()
        prof.scores = Scores(rating_score=4.0, tag_quality_score=80.0)
        result = scorer.analyze(prof)
        assert result["quality"] == 76.0

    def test_analyze_no_scores(self):
        scorer = QualityScorer()
        prof = Professor()
        result = scorer.analyze(prof)
        assert result["quality"] == 0.0
