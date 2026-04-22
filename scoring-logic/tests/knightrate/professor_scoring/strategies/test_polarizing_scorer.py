import pytest
from src.knightrate.professor_scoring.strategies.polarizing_scorer import PolarizingScorer
from src.knightrate.professor_scoring.models import Professor, Review

class TestPolarizingScorer:
    def test_initialization(self):
        scorer = PolarizingScorer()
        assert scorer.metric_name == "isPolarizing"

    def test_is_polarizing_true(self):
        scorer = PolarizingScorer()
        # high variance logic > 3.75
        # scores = [5, 1, 5, 1]. avg = 3. var = ((2)^2 + (-2)^2 + (2)^2 + (-2)^2)/4 = 16/4 = 4.0
        prof = Professor(reviews=[
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0),
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=1.0),
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0),
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=1.0)
        ])
        result = scorer.analyze(prof)
        assert result["isPolarizing"] is True

    def test_is_polarizing_false(self):
        scorer = PolarizingScorer()
        # low variance logic <= 3.75
        # scores = [4, 5, 4, 5]. avg = 4.5. var = (0.25+0.25+0.25+0.25)/4 = 0.25
        prof = Professor(reviews=[
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=4.0),
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0),
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=4.0),
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0)
        ])
        result = scorer.analyze(prof)
        assert result["isPolarizing"] is False

    def test_is_polarizing_few_reviews(self):
        scorer = PolarizingScorer()
        prof = Professor(reviews=[Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0)])
        result = scorer.analyze(prof)
        assert result["isPolarizing"] is False
