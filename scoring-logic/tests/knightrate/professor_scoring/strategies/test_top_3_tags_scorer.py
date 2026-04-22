import pytest
from src.knightrate.professor_scoring.strategies.top_3_tags_scorer import Top3TagsScorer
from src.knightrate.professor_scoring.models import Professor, Review

class TestTop3TagsScorer:
    def test_initialization(self):
        scorer = Top3TagsScorer()
        assert scorer.metric_name == "topThreeTags"

    def test_analyze_top_3(self):
        scorer = Top3TagsScorer()
        # tags: "tough", "tough", "tough", "boring", "boring", "long"
        prof = Professor(reviews=[
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, rating_tags=["tough", "boring", "long"]),
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, rating_tags=["tough", "boring"]),
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, rating_tags=["tough"])
        ])
        result = scorer.analyze(prof)
        # Note: Alphabetical tie-breaking puts 'Boring' before 'Long' anyway
        assert result["topThreeTags"] == ["Tough", "Boring", "Long"]
        
    def test_analyze_fewer_than_3(self):
        scorer = Top3TagsScorer()
        prof = Professor(reviews=[
            Review(clarity_rating=5.0, difficulty_rating=3.0, helpful_rating=5.0, rating_tags=["fun"])
        ])
        result = scorer.analyze(prof)
        assert result["topThreeTags"] == ["Fun"]
        
    def test_analyze_no_reviews(self):
        scorer = Top3TagsScorer()
        prof = Professor(reviews=[])
        result = scorer.analyze(prof)
        assert result["topThreeTags"] == []
