from .base_strategy import ScoringStrategy
from models import Professor

class Top3TagsScorer(ScoringStrategy):
    def __init__(self):
        self.metric_name = "topThreeTags"

    def analyze(self, professor: Professor) -> dict:
        top_three = self._get_top_three_tags(professor)
        return {self.metric_name: top_three}
    
    def _get_top_three_tags(self, professor: Professor) -> list[str]:
        all_tags = {}
        for rev in professor.reviews:
            if not rev.rating_tags:
                continue
            for tag in rev.rating_tags:
                t = tag.title()
                all_tags[t] = all_tags.get(t, 0) + 1
        
        # Sort descending by count, then ascending alphabetically to break ties cleanly
        top_3: list[tuple[str, int]] = sorted(all_tags.items(), key=lambda x: (-x[1], x[0]))[:3]
        return [t[0] for t in top_3]


    