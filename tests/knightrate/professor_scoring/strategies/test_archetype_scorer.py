import pytest
from knightrate.professor_scoring.strategies.archetype_scorer import ArchetypeScorer
from knightrate.professor_scoring.models import Professor, Scores

class TestArchetypeScorer:
    def test_initialization(self):
        scorer = ArchetypeScorer()
        assert scorer.metric_name == "archetype"

    # def test_analyze_mastermind(self):
    #     scorer = ArchetypeScorer()
    #     prof = Professor()
    #     prof.scores = Scores(quality=60.0, difficulty=60.0)
    #     result = scorer.analyze(prof)
    #     assert result["archetype"] == "The Mastermind"

    # def test_analyze_unicorn(self):
    #     scorer = ArchetypeScorer()
    #     prof = Professor()
    #     prof.scores = Scores(quality=60.0, difficulty=40.0)
    #     result = scorer.analyze(prof)
    #     assert result["archetype"] == "The Unicorn"

    # def test_analyze_saboteur(self):
    #     scorer = ArchetypeScorer()
    #     prof = Professor()
    #     prof.scores = Scores(quality=40.0, difficulty=60.0)
    #     result = scorer.analyze(prof)
    #     assert result["archetype"] == "The Saboteur"

    # def test_analyze_npc(self):
    #     scorer = ArchetypeScorer()
    #     prof = Professor()
    #     prof.scores = Scores(quality=40.0, difficulty=40.0)
    #     result = scorer.analyze(prof)
    #     assert result["archetype"] == "The NPC"

    # def test_analyze_no_scores(self):
    #     scorer = ArchetypeScorer()
    #     prof = Professor()
    #     result = scorer.analyze(prof)
    #     assert result["archetype"] == "The NPC"
