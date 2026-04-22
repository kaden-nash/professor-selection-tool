import pytest
from src.knightrate.professor_scoring.strategies.rating_scorer import RatingScorer
from src.knightrate.professor_scoring.models import Professor

class TestRatingScorer:
    def test_rating_scorer_initialization(self):
        scorer = RatingScorer()
        assert scorer.metric_name == "ratingScore"

    def test_extract_rating_valid(self):
        scorer = RatingScorer()
        prof = Professor(avg_rating=4.5)
        assert scorer._extract_rating(prof) == 4.5

    def test_extract_rating_missing(self):
        scorer = RatingScorer()
        prof = Professor()
        assert scorer._extract_rating(prof) == 0.0

    def test_extract_rating_string(self):
        scorer = RatingScorer()
        prof = Professor(avg_rating=4.2)
        assert scorer._extract_rating(prof) == 4.2

    def test_analyze_rating(self):
        scorer = RatingScorer()
        prof = Professor(avg_rating=3.8)
        result = scorer.analyze(prof)
        assert result == {"ratingScore": 3.8}

    def test_analyze_rating_missing(self):
        scorer = RatingScorer()
        prof = Professor()
        result = scorer.analyze(prof)
        assert result == {"ratingScore": 0.0}
