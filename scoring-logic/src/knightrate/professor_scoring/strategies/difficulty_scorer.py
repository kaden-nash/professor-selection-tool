from .base_strategy import ScoringStrategy
from ..models import Professor

class RawDifficultyScorer(ScoringStrategy):
    """Scores a professor based on their average difficulty. Between 1-5"""

    def __init__(self):
        self.metric_name = "rawDifficultyScore"

    def analyze(self, professor: Professor) -> dict:
        """Analyzes the difficulty rating."""
        score = self._extract_difficulty(professor)
        return {self.metric_name: score}

    def _extract_difficulty(self, professor: Professor) -> float:
        """Extracts the difficulty score, defaulting to 0.0 if not found."""
        return float(professor.avg_difficulty)
