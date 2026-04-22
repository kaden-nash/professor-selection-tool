import pytest
from src.knightrate.professor_scoring.strategies.tag_friction_scorer import TagFrictionScorer
from src.knightrate.professor_scoring.models import Professor, Review

class TestTagFrictionScorer:
    def test_initialization(self):
        scorer = TagFrictionScorer()
        assert scorer.metric_name == "tagFrictionScore"

    def test_analyze_with_tags(self):
        scorer = TagFrictionScorer()
        reviews = [
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, rating_tags=["Tough Grader"]),
            Review(clarity_rating=4.0, difficulty_rating=2.0, helpful_rating=4.0, rating_tags=["extra credit", "group projects", "random"]),
        ]
        prof = Professor(reviews=reviews)
        result = scorer.analyze(prof)
        assert "tagFrictionScore" in result
        assert result["tagFrictionScore"] == 50.0

    def test_analyze_empty_tags(self):
        scorer = TagFrictionScorer()
        prof = Professor(reviews=[Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0)])
        result = scorer.analyze(prof)
        assert result["tagFrictionScore"] == 50.0

    def test_analyze_no_reviews(self):
        scorer = TagFrictionScorer()
        prof = Professor()
        result = scorer.analyze(prof)
        assert result["tagFrictionScore"] == 50.0
