from .base_strategy import ScoringStrategy
from ..models import Professor

class OverallScorer(ScoringStrategy):
    def __init__(self):
        self.metric_name = "overall"

    def analyze(self, professor: Professor) -> dict[str, float]:
        quality_score = professor.scores.quality if professor.scores else 0.0
        wta_score = professor.scores.would_take_again_score if professor.scores else 0.0
        if wta_score == "Unavailable":
            wta_score = 50
        overall = self._get_overall_score(quality_score, wta_score)
        return {self.metric_name: overall}
    
    def _get_overall_score(self, quality_score: float, wta_score: float) -> float:
        """Calculates a composite overall score from the quality score and wta score."""
        wta_percent = (wta_score/100)
        adj = (wta_percent - 0.5) * 20
        final = quality_score + adj
        return round(max(0, min(100, final)), 2)