from ..models import Professor
from ..global_stats.base_statistic import StatisticStrategy

class AverageOverallStat(StatisticStrategy):
    """Calculates the average overall score across every professor."""
    
    def __init__(self):
        self.metric_name = "avgOverall"

    def calculate(self, professors: list[Professor]) -> float:
        valid_overall = [p.scores.overall for p in professors if p.scores]
        overall_avg = sum(valid_overall) / len(valid_overall) if valid_overall else 0.0
        return round(overall_avg, 2)