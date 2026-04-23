from .base_strategy import ScoringStrategy
from ..models import Professor, GlobalStatistics

class ArchetypeScorer(ScoringStrategy):
    """Calculates archtype. Can be: The Unicorn, The Mastermind, The Saboteur, The NPC"""

    def __init__(self):
        self.metric_name = "archetype"

    def analyze(self, professor: Professor, global_stats: GlobalStatistics) -> dict[str, str]:
        q_score = professor.scores.quality if professor.scores else 0.0
        d_score = professor.scores.difficulty if professor.scores else 0.0
        archetype = self._get_2x2_archetype(q_score, d_score, global_stats)
        return {self.metric_name: archetype}

    def _get_2x2_archetype(self, q_score: float, d_score: float, global_stats: GlobalStatistics):
        """Calculates archetype for a single professor."""
        global_avg_difficulty = global_stats.avg_difficulty
        global_avg_quality = global_stats.avg_quality
        arbitrary_value = 5
        if q_score >= global_avg_quality:
            return "The Mastermind" if d_score >= global_avg_difficulty - arbitrary_value else "The Unicorn"
        else: # if d_score >= global_avg_difficulty - 5
            return "The Saboteur" if d_score >= global_avg_difficulty + (arbitrary_value + (arbitrary_value/2)) else "The NPC" # if d_score >= global_avg_difficulty + 7.5

