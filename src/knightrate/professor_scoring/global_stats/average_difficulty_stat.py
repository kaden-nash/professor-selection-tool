from ..models import Professor
from ..global_stats.base_statistic import StatisticStrategy

class AverageDifficultyStat(StatisticStrategy):
    def __init__(self):
        self.metric_name = "avgDifficulty"

    def calculate(self, professors: list[Professor]) -> float:
        valid_difficulty = [p.scores.difficulty for p in professors if p.scores]
        difficulty_avg = sum(valid_difficulty) / len(valid_difficulty) if valid_difficulty else 0.0
        return round(difficulty_avg, 2)