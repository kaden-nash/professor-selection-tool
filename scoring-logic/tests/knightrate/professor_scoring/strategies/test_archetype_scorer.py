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
        prof.scores = Scores(quality=55.0, difficulty=55.0)  # Q>=55, D>=45
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The Mastermind"

    def test_analyze_unicorn(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        prof.scores = Scores(quality=55.0, difficulty=40.0)  # Q>=55, D<45
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The Unicorn"

    def test_analyze_saboteur(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        prof.scores = Scores(quality=40.0, difficulty=60.0)  # Q<55, D>=57.5
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The Saboteur"

    def test_analyze_npc(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        prof.scores = Scores(quality=40.0, difficulty=40.0)  # Q<55, D<57.5
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The NPC"

    def test_analyze_no_scores(self):
        scorer = ArchetypeScorer()
        prof = Professor()
        result = scorer.analyze(prof, self._get_dummy_stats())
        assert result["archetype"] == "The NPC"

