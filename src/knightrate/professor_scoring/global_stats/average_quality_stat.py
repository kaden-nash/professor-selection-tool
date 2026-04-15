from models import Professor
from global_stats.base_statistic import StatisticStrategy

class AverageQualityStat(StatisticStrategy):
    def __init__(self):
        self.metric_name = "avgQuality"

    def calculate(self, professors: list[Professor]) -> float:
        valid_quality = [p.scores.quality for p in professors if p.scores]
        quality_avg = sum(valid_quality) / len(valid_quality) if valid_quality else 0.0
        return round(quality_avg, 2)