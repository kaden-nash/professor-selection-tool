from .base_strategy import ScoringStrategy
from ..models import Professor

class TagQualityScorer(ScoringStrategy):
    """Scores a professor based on their quality tags."""

    quality_weights = {
        "gives good feedback": 1, "respected": 1, "inspirational": 1,
        "amazing lectures": 1, "hilarious": 1, "caring": 1,
        "accessible outside class": 1, "clear grading criteria": 1,
        "beware of pop quizzes": -1, "online savvy": 1
    }

    def __init__(self):
        self.metric_name = "tagQualityScore"

    def analyze(self, professor: Professor) -> dict[str, float]:
        tags = self._get_tags(professor)
        score = self._get_quality_score(tags)
        return {self.metric_name: score}

    def _get_tags(self, professor: Professor):
        all_tags = []
        for rev in professor.reviews:
            for tag in rev.rating_tags:
                all_tags.append(tag.lower())
        return all_tags
        
    def _get_quality_score(self, tags):
        scores = [self.quality_weights[t] for t in tags if t in self.quality_weights]
        avg = sum(scores) / len(scores) if scores else 0
        return round(float((avg + 1) * 50), 2)
