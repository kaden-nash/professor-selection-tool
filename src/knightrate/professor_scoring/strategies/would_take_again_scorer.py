from .base_strategy import ScoringStrategy
from ..models import Professor

class WouldTakeAgainScorer(ScoringStrategy):
    """Scores a professor based on the percentage of students that would take them again."""

    def __init__(self):
        self.metric_name = "wouldTakeAgainScore"

    def analyze(self, professor: Professor) -> dict[str, float | str]:
        """Analyzes the would take again scores for the professor."""
        if professor.would_take_again_percent < 0:
            return {self.metric_name: "Unavailable"}
        score = self._extract_would_take_again(professor)
        return {self.metric_name: score}

    def _extract_would_take_again(self, professor: Professor) -> float | str:
        """Calculates average would take again scores."""
        yeses = 0
        total_valid = 0
        counter = 1
        YES_THRESHOLD = 4
        for rev in professor.reviews:
            if rev.would_take_again is not None:
                total_valid += 1
                if rev.would_take_again == 1:
                    yeses += 1
            else: # this offsets the strange occurrence where bad professors have very few reviews where students opt to answer the "would take again" question.
                if rev.helpful_rating < YES_THRESHOLD:
                    total_valid += 1
                
                    
        if total_valid == 0:
            return "Unavailable"
            # return 0.0
            
        percent_yes = yeses / total_valid
        return round(float(percent_yes) * 100, 2)
