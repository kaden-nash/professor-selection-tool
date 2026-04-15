from .base_strategy import ScoringStrategy
from ..models import Professor

class ArchetypeScorer(ScoringStrategy):
    def __init__(self):
        self.metric_name = "archetype"

    def analyze(self, professor: Professor) -> dict[str, str]:
        q_score = professor.scores.quality if professor.scores else 0.0
        d_score = professor.scores.difficulty if professor.scores else 0.0
        archetype = self.get_2x2_archetype(q_score, d_score)
        return {self.metric_name: archetype}

    def get_2x2_archetype(self, q_score: float, f_score: float):
        global_avg_difficulty = 52.6
        global_avg_quality = 73.01
        arbitrary_value = 5
        if q_score >= global_avg_quality + arbitrary_value:
            return "The Mastermind" if f_score >= global_avg_difficulty - arbitrary_value else "The Unicorn"
        else:
            return "The Saboteur" if f_score >= global_avg_difficulty + (arbitrary_value + (arbitrary_value/2)) else "The NPC" # if f_score >= global_avg_difficulty + 7.5

