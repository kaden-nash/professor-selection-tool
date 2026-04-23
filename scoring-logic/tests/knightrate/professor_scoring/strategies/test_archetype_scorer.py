import pytest
from src.knightrate.professor_scoring.strategies.archetype_scorer import ArchetypeScorer
from src.knightrate.professor_scoring.models import Professor, Scores, GlobalStatistics

class TestArchetypeScorer:
    def test_initialization(self):
        scorer = ArchetypeScorer()
        assert scorer.metric_name == "archetype"

    def _get_dummy_stats(self):
        return GlobalStatistics(avgQuality=50.0, avgDifficulty=50.0)

    def test_analyze_mastermind(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        prof.scores = Scores(quality=50.0, difficulty=45.0)  # Q>=50, D>=45
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The Mastermind"

    def test_analyze_unicorn(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        prof.scores = Scores(quality=50.0, difficulty=44.9)  # Q>=50, D<45
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The Unicorn"

    def test_analyze_saboteur(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        prof.scores = Scores(quality=49.9, difficulty=57.5)  # Q<50, D>=57.5
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The Saboteur"

    def test_analyze_npc(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        prof.scores = Scores(quality=49.9, difficulty=57.4)  # Q<50, D<57.5
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The NPC"

    def test_analyze_no_scores(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The NPC"

