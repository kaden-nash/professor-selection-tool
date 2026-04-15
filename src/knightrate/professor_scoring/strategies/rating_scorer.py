from .base_strategy import ScoringStrategy
from ..models import Professor

class RatingScorer(ScoringStrategy):
    """Scores a professor based on their average rating."""

    def __init__(self):
        self.metric_name = "ratingScore"

    def analyze(self, professor: Professor) -> dict:
        """Analyzes the average rating."""
        score = self._extract_rating(professor)
        return {self.metric_name: score}

    def _extract_rating(self, professor: Professor) -> float:
        """Extracts the rating score, defaulting to 0.0 if not found."""
        return float(professor.avg_rating)
