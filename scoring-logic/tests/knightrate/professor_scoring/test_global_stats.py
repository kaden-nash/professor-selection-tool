import pytest
from src.knightrate.professor_scoring.models import Professor, Scores
from src.knightrate.professor_scoring.global_stats.average_overall_stat import AverageOverallStat
from src.knightrate.professor_scoring.global_stats.average_quality_stat import AverageQualityStat
from src.knightrate.professor_scoring.global_stats.average_difficulty_stat import AverageDifficultyStat
from src.knightrate.professor_scoring.global_stats.average_wta_stat import AverageWouldTakeAgainStat

class TestGlobalStats:
    def test_average_overall_stat(self):
        stat = AverageOverallStat()
        
        prof1 = Professor(firstName="Test")
        prof1.scores = Scores(overall=4.0)
        
        prof2 = Professor(firstName="Test2")
        prof2.scores = Scores(overall=2.0)
        
        prof3 = Professor(firstName="Test3")
        # No scores for prof3
        
        result = stat.calculate([prof1, prof2, prof3])
        assert isinstance(result, float)
        assert result == 3.0

    def test_average_overall_stat_zero(self):
        stat = AverageOverallStat()
        prof1 = Professor(firstName="Test")
        result = stat.calculate([prof1])
        assert result == 0.0

    def test_average_quality_stat(self):
        stat = AverageQualityStat()
        prof1 = Professor(firstName="Test", scores=Scores(quality=3.5))
        prof2 = Professor(firstName="Test", scores=Scores(quality=4.5))
        result = stat.calculate([prof1, prof2])
        assert result == 4.0

    def test_average_difficulty_stat(self):
        stat = AverageDifficultyStat()
        prof1 = Professor(firstName="Test", scores=Scores(difficulty=1.5))
        prof2 = Professor(firstName="Test", scores=Scores(difficulty=2.5))
        result = stat.calculate([prof1, prof2])
        assert result == 2.0

    def test_average_wta_stat_with_unavailable(self):
        stat = AverageWouldTakeAgainStat()
        prof1 = Professor(firstName="Test", scores=Scores(would_take_again_score=80.0))
        prof2 = Professor(firstName="Test", scores=Scores(would_take_again_score="Unavailable"))
        prof3 = Professor(firstName="Test", scores=Scores(would_take_again_score=100.0))
        
        result = stat.calculate([prof1, prof2, prof3])
        assert result == 90.0

    def test_average_wta_stat_all_unavailable(self):
        stat = AverageWouldTakeAgainStat()
        prof1 = Professor(firstName="Test", scores=Scores(would_take_again_score="Unavailable"))
        result = stat.calculate([prof1])
        assert result == 0.0
