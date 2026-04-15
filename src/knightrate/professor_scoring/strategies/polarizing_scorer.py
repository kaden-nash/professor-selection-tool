from .base_strategy import ScoringStrategy
from ..models import Professor

class PolarizingScorer(ScoringStrategy):
    def __init__(self):
        self.metric_name = "isPolarizing"

    def analyze(self, professor: Professor) -> dict[str, bool]:
        scores = self._get_scores(professor)
        verdict = self._is_polarizing(scores)
        return {self.metric_name: verdict}

    def _is_polarizing(self, scores: list[float]) -> bool:
        if len(scores) < 2: return False
        avg = sum(scores) / len(scores)
        var = sum((s - avg) ** 2 for s in scores) / len(scores)
        return var > 2.5

    def _get_scores(self, professor: Professor) -> list[float]:
        scores = []
        for rev in professor.reviews:
            scores.append(rev.helpful_rating)
        return scores