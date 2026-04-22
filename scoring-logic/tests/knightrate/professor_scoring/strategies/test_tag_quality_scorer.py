import pytest
from src.knightrate.professor_scoring.strategies.tag_quality_scorer import TagQualityScorer
from src.knightrate.professor_scoring.models import Professor, Review

class TestTagQualityScorer:
    def test_initialization(self):
        scorer = TagQualityScorer()
        assert scorer.metric_name == "tagQualityScore"

    def test_analyze_with_tags(self):
        scorer = TagQualityScorer()
        reviews = [
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, rating_tags=["GIVES GOOD FEEDBACK"]),
            Review(clarity_rating=4.0, difficulty_rating=2.0, helpful_rating=4.0, rating_tags=["RESPECTED", "beware of pop quizzes", "random tag"]),
        ]
        prof = Professor(reviews=reviews)
        result = scorer.analyze(prof)
        assert "tagQualityScore" in result
        assert result["tagQualityScore"] == 66.67

    def test_analyze_empty_tags(self):
        scorer = TagQualityScorer()
        prof = Professor(reviews=[Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0)])
        result = scorer.analyze(prof)
        assert result["tagQualityScore"] == 50.0

    def test_analyze_no_reviews(self):
        scorer = TagQualityScorer()
        prof = Professor()
        result = scorer.analyze(prof)
        assert result["tagQualityScore"] == 50.0
