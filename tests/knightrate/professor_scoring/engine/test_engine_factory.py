import pytest
from knightrate.professor_scoring.engine.engine_factory import ScoringEngineFactory
from knightrate.professor_scoring.engine.scoring_engine import ScoringEngine
from knightrate.professor_scoring.strategies.difficulty_scorer import RawDifficultyScorer
from knightrate.professor_scoring.strategies.rating_scorer import RatingScorer
from knightrate.professor_scoring.strategies.would_take_again_scorer import WouldTakeAgainScorer
from knightrate.professor_scoring.strategies.tag_friction_scorer import TagFrictionScorer
from knightrate.professor_scoring.strategies.tag_quality_scorer import TagQualityScorer

from knightrate.professor_scoring.strategies.combined_difficulty_scorer import DifficultyScorer
from knightrate.professor_scoring.strategies.quality_scorer import QualityScorer
from knightrate.professor_scoring.strategies.overall_scorer import OverallScorer
from knightrate.professor_scoring.strategies.archetype_scorer import ArchetypeScorer

class TestScoringEngineFactory:
    def test_create_first_round_engine(self):
        factory = ScoringEngineFactory()
        engine = factory.create_first_round_engine()
        assert isinstance(engine, ScoringEngine)
        assert len(engine.strategies) == 8
        
        strategy_types = [type(s) for s in engine.strategies]
        assert RawDifficultyScorer in strategy_types
        assert RatingScorer in strategy_types
        assert WouldTakeAgainScorer in strategy_types
        assert TagFrictionScorer in strategy_types
        assert TagQualityScorer in strategy_types

    def test_create_second_round_engine(self):
        factory = ScoringEngineFactory()
        engine = factory.create_second_round_engine()
        assert isinstance(engine, ScoringEngine)
        assert len(engine.strategies) == 4
        
        strategy_types = [type(s) for s in engine.strategies]
        assert DifficultyScorer in strategy_types
        assert QualityScorer in strategy_types
        assert OverallScorer in strategy_types
        assert ArchetypeScorer in strategy_types
