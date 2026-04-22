from .base_strategy import ScoringStrategy
from ..models import Professor

class QualityScorer(ScoringStrategy):
    """Calculates a composite quality score from the avg_quality_score on rmp and the tag score. Always between 0-100."""

    def __init__(self):
        self.metric_name = "quality"

    def analyze(self, professor: Professor) -> dict:
        rating_score = professor.scores.rating_score if professor.scores else 0.0
        tag_score = professor.scores.tag_quality_score if professor.scores else 0.0
        score = self._get_final_quality(rating_score, tag_score)
        return {self.metric_name: score}

    def _get_final_quality(self, rating_score: float, tag_score: float):
        """Calculates a composite quality score from the avg_quality_score on rmp and the tag score."""
        norm_rating = self._normalize_rating(rating_score)
        val = (norm_rating * 0.8) + (tag_score * 0.2)
        return round(max(0.0, val), 2)

    def _normalize_rating(self, val: float):
        """Normalize rating so it is always between 0 and 100."""
        return (val - 1) * 25