from .base_strategy import ScoringStrategy
from models import Professor

class TagFrictionScorer(ScoringStrategy):
    """Scores a professor based on their friction tags."""

    friction_weights = {
        "tough grader": 1, "get ready to read": 1, "lots of homework": 1,
        "graded by few things": 1, "test heavy": 1, "so many papers": 1,
        "group projects": 0, "extra credit": -1, "participation matters": 0,
        "skip class? you won't pass": 0, "lecture heavy": 0,
    }

    # "Online Savvy"


    def __init__(self):
        self.metric_name = "tagFrictionScore"

    def analyze(self, professor: Professor) -> dict[str, float]:
        tags = self._get_tags(professor)
        score = self._get_friction_score(tags)
        return {self.metric_name: score}

    def _get_tags(self, professor: Professor):
        all_tags = []
        for rev in professor.reviews:
            for tag in rev.rating_tags:
                all_tags.append(tag.lower())
        return all_tags

    def _get_friction_score(self, tags):
        scores = [self.friction_weights[t] for t in tags if t in self.friction_weights]
        avg = sum(scores) / len(scores) if scores else 0
        return round(float((avg + 1) * 50), 2)