import pytest
from unittest.mock import patch
from src.knightrate.professor_scoring.strategies.would_take_again_scorer import WouldTakeAgainScorer
from src.knightrate.professor_scoring.models import Professor, Review

class TestWouldTakeAgainScorer:
    def test_initialization(self):
        scorer = WouldTakeAgainScorer()
        assert scorer.metric_name == "wouldTakeAgainScore"

    def test_extract_valid(self):
        scorer = WouldTakeAgainScorer()
        reviews = [
            Review(clarityRating=5.0, difficultyRating=3.0, helpfulRating=5.0, wouldTakeAgain=1),
            Review(clarityRating=4.0, difficultyRating=2.0, helpfulRating=4.0, wouldTakeAgain=0),
            Review(clarityRating=5.0, difficultyRating=4.0, helpfulRating=5.0, wouldTakeAgain=1)
        ]
        prof = Professor(reviews=reviews)
        assert scorer._extract_would_take_again(prof) == 66.67

    @patch('random.randint')
    def test_extract_with_none_values(self, mock_randint):
        mock_randint.return_value = 100  # Will fail the rand <= 75 check explicitly so total_valid stays 1
        scorer = WouldTakeAgainScorer()
        reviews = [
            Review(clarityRating=5.0, difficultyRating=3.0, helpfulRating=5.0, wouldTakeAgain=1),
            Review(clarityRating=4.0, difficultyRating=2.0, helpfulRating=4.0, wouldTakeAgain=None),
            Review(clarityRating=5.0, difficultyRating=4.0, helpfulRating=5.0, wouldTakeAgain=None)
        ]
        prof = Professor(reviews=reviews)
        # 1 valid vote of yes, total valid votes = 1
        assert scorer._extract_would_take_again(prof) == 100.0

    @patch('random.randint')
    def test_extract_all_none_values(self, mock_randint):
        mock_randint.return_value = 100 # Keep valid count at 0
        scorer = WouldTakeAgainScorer()
        reviews = [
            Review(clarityRating=5.0, difficultyRating=3.0, helpfulRating=5.0, wouldTakeAgain=None)
        ]
        prof = Professor(reviews=reviews)
        assert scorer._extract_would_take_again(prof) == "Unavailable"

    def test_extract_no_reviews(self):
        scorer = WouldTakeAgainScorer()
        prof = Professor(reviews=[])
        assert scorer._extract_would_take_again(prof) == "Unavailable"

    def test_analyze_unavailable(self):
        scorer = WouldTakeAgainScorer()
        prof = Professor(would_take_again_percent=-1)
        result = scorer.analyze(prof)
        assert result["wouldTakeAgainScore"] == "Unavailable"

    def test_analyze(self):
        scorer = WouldTakeAgainScorer()
        reviews = [
            Review(clarityRating=5.0, difficultyRating=3.0, helpfulRating=5.0, wouldTakeAgain=1),
            Review(clarityRating=4.0, difficultyRating=2.0, helpfulRating=4.0, wouldTakeAgain=0)
        ]
        prof = Professor(reviews=reviews, would_take_again_percent=0.5)
        result = scorer.analyze(prof)
        assert result == {"wouldTakeAgainScore": 50.0}
