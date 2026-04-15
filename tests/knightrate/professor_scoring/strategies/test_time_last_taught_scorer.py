import pytest
from knightrate.professor_scoring.strategies.time_last_taught_scorer import TimeLastTaughtScorer
from knightrate.professor_scoring.models import Professor, Review

class TestTimeLastTaughtScorer:
    def test_initialization(self):
        scorer = TimeLastTaughtScorer()
        assert scorer.metric_name == "timeLastTaught"

    def test_analyze_valid_summer(self):
        scorer = TimeLastTaughtScorer()
        prof = Professor(reviews=[Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, date="2023-07-28 17:08:31 +0000 UTC")])
        result = scorer.analyze(prof)
        assert result["timeLastTaught"] == "Summer 2023"

    def test_analyze_valid_spring(self):
        scorer = TimeLastTaughtScorer()
        prof = Professor(reviews=[Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, date="2021-03-28 17:08:31 +0000 UTC")])
        result = scorer.analyze(prof)
        assert result["timeLastTaught"] == "Spring 2021"

    def test_analyze_valid_fall(self):
        scorer = TimeLastTaughtScorer()
        prof = Professor(reviews=[Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, date="2022-11-28 17:08:31 +0000 UTC")])
        result = scorer.analyze(prof)
        assert result["timeLastTaught"] == "Fall 2022"

    def test_analyze_unknown_date_format(self):
        scorer = TimeLastTaughtScorer()
        prof = Professor(reviews=[Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, date="Unknown Format")])
        result = scorer.analyze(prof)
        assert result["timeLastTaught"] == "Unknown"

    def test_analyze_no_reviews(self):
        scorer = TimeLastTaughtScorer()
        prof = Professor(reviews=[])
        result = scorer.analyze(prof)
        assert result["timeLastTaught"] == "Unknown"
