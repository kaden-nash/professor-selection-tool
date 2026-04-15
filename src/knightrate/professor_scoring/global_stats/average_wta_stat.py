from ..models import Professor
from ..global_stats.base_statistic import StatisticStrategy

class AverageWouldTakeAgainStat(StatisticStrategy):
    def __init__(self):
        self.metric_name = "avgWouldTakeAgain"

    def calculate(self, professors: list[Professor]) -> float:
        valid_wta = [p.scores.would_take_again_score for p in professors if p.scores and p.scores.would_take_again_score != "Unavailable"]
        wta_avg = sum(valid_wta) / len(valid_wta) if valid_wta else 0.0
        return round(wta_avg, 2)