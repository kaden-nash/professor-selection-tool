import json
import os
import sys

# Ensure professor_scoring's own sub-modules are resolvable when invoked
# from the project root. This is the single controlled sys.path addition
# needed because the scoring sub-modules use bare imports (e.g. 'from models').
_SCORING_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCORING_DIR not in sys.path:
    sys.path.insert(0, _SCORING_DIR)

from engine.engine_factory import ScoringEngineFactory  # noqa: E402
from models import Professor, GlobalStatistics  # noqa: E402


class ProfessorScoringRunner:
    """Orchestrates the professor scoring pipeline."""

    def __init__(self, root_dir: str):
        self._root_dir = root_dir

    def run(self) -> None:
        """Runs the full professor scoring pipeline."""
        input_path = os.path.join(self._root_dir, "data_fixing", "professor_data.json")
        output_path = os.path.join(self._root_dir, "professor_scoring", "professor_ratings.json")
        stats_path = os.path.join(self._root_dir, "professor_scoring", "global_statistics.json")

        data = self._load_data(input_path)
        data = self._run_scoring(data)
        global_stats = self._calculate_statistics(data)

        self._save_data(output_path, data)
        self._save_statistics(stats_path, global_stats)
        print(f"Scoring complete. Results saved to {output_path} and {stats_path}")

    def _load_data(self, path: str) -> list:
        """Loads the professor JSON data from disk."""
        abs_path = os.path.abspath(path)
        with open(abs_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        return [Professor(**d) if isinstance(d, dict) else d for d in raw_data]

    def _run_scoring(self, data: list) -> list:
        """Applies first and second round scoring engines to the data."""
        factory = ScoringEngineFactory()
        data = factory.create_first_round_engine().process_data(data)
        data = factory.create_second_round_engine().process_data(data)
        return data

    def _calculate_statistics(self, data: list) -> GlobalStatistics:
        """Calculates global statistics from the scored professor data."""
        factory = ScoringEngineFactory()
        return factory.create_global_stat_engine().calculate_statistics(data)

    def _save_data(self, path: str, data: list) -> None:
        """Saves the processed professor data to JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json_data = [
                p.model_dump(by_alias=True) if isinstance(p, Professor) else p for p in data
            ]
            json.dump(json_data, f, indent=4)

    def _save_statistics(self, path: str, stats: GlobalStatistics) -> None:
        """Saves the global statistics to JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stats.model_dump(), f, indent=4)
