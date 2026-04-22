import pytest
from src.knightrate.professor_scoring.strategies.overall_scorer import OverallScorer
from src.knightrate.professor_scoring.models import Professor, Scores

class TestOverallScorer:
    def test_initialization(self):
        scorer = OverallScorer()
        assert scorer.metric_name == "overall"

    def test_analyze_overall(self):
        scorer = OverallScorer()
        prof = Professor()
        prof.scores = Scores(quality=75.0, would_take_again_score=80.0)
        result = scorer.analyze(prof)
        assert result["overall"] == 81.0

    def test_analyze_boundaries_high(self):
        scorer = OverallScorer()
        prof = Professor()
        prof.scores = Scores(quality=99.0, would_take_again_score=90.0)
        result = scorer.analyze(prof)
        assert result["overall"] == 100.0

    def test_analyze_boundaries_low(self):
        scorer = OverallScorer()
        prof = Professor()
        prof.scores = Scores(quality=2.0, would_take_again_score=10.0)
        result = scorer.analyze(prof)
        assert result["overall"] == 0.0

    def test_analyze_unavailable_wta(self):
        scorer = OverallScorer()
        prof = Professor()
        # wta = 'Unavailable' should map to 0.5. adj = 0.
        prof.scores = Scores(quality=80.0, would_take_again_score="Unavailable")
        result = scorer.analyze(prof)
        assert result["overall"] == 80.0

    def test_analyze_no_scores(self):
        scorer = OverallScorer()
        prof = Professor()
        result = scorer.analyze(prof)
        assert result["overall"] == 0.0
