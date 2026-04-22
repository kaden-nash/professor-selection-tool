from ..engine.scoring_engine import ScoringEngine
from ..strategies.difficulty_scorer import RawDifficultyScorer
from ..strategies.rating_scorer import RatingScorer
from ..strategies.would_take_again_scorer import WouldTakeAgainScorer
from ..strategies.tag_friction_scorer import TagFrictionScorer
from ..strategies.tag_quality_scorer import TagQualityScorer
from ..strategies.top_3_tags_scorer import Top3TagsScorer
from ..strategies.time_last_taught_scorer import TimeLastTaughtScorer
from ..strategies.polarizing_scorer import PolarizingScorer

from ..strategies.combined_difficulty_scorer import DifficultyScorer
from ..strategies.quality_scorer import QualityScorer
from ..strategies.overall_scorer import OverallScorer
from ..strategies.archetype_scorer import ArchetypeScorer

from ..global_stats.average_overall_stat import AverageOverallStat
from ..global_stats.average_quality_stat import AverageQualityStat
from ..global_stats.average_difficulty_stat import AverageDifficultyStat
from ..global_stats.average_wta_stat import AverageWouldTakeAgainStat


class ScoringEngineFactory:
    """Factory class for creating and configuring a ScoringEngine."""
    
    @staticmethod
    def create_first_round_engine() -> ScoringEngine:
        """Initializes and returns configured ScoringEngine."""
        engine = ScoringEngine()
        engine.register_strategy(RawDifficultyScorer())
        engine.register_strategy(RatingScorer())
        engine.register_strategy(WouldTakeAgainScorer())
        engine.register_strategy(TagFrictionScorer())
        engine.register_strategy(TagQualityScorer())
        
        # New base data scorers
        engine.register_strategy(Top3TagsScorer())
        engine.register_strategy(TimeLastTaughtScorer())
        engine.register_strategy(PolarizingScorer())
        return engine
    
    @staticmethod
    def create_second_round_engine() -> ScoringEngine:
        engine = ScoringEngine()
        engine.register_strategy(DifficultyScorer())
        engine.register_strategy(QualityScorer())
        engine.register_strategy(OverallScorer())
        return engine
    
    @staticmethod
    def create_third_round_engine() -> ScoringEngine:
        engine = ScoringEngine()
        engine.register_strategy(ArchetypeScorer())
        return engine

    @staticmethod
    def create_global_stat_engine() -> ScoringEngine:
        engine = ScoringEngine()
        engine.register_statistic(AverageWouldTakeAgainStat())
        engine.register_statistic(AverageDifficultyStat())
        engine.register_statistic(AverageQualityStat())
        engine.register_statistic(AverageOverallStat())
        return engine