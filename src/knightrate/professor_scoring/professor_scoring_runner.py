import json
import os

from .engine.engine_factory import ScoringEngineFactory
from .models import Professor, GlobalStatistics
from .send_to_db import MongoUploader

class ProfessorScoringRunner:
    """Orchestrates the professor scoring pipeline."""

    def __init__(self, root_dir: str):
        self._root_dir = root_dir

    def run(self) -> None:
        """Runs the full professor scoring pipeline."""
        input_path = os.path.join(self._root_dir, "src", "knightrate", "data_fixing", "professor_data.json")
        self.output_path = os.path.join(self._root_dir, "src", "knightrate", "professor_scoring", "professor_ratings.json")
        self.stats_path = os.path.join(self._root_dir, "src", "knightrate", "professor_scoring", "global_statistics.json")

        data = self._load_data(input_path)
        data = self._run_scoring(data)
        global_stats = self._calculate_statistics(data)
        data = self._run_scoring_with_global_stats(data, global_stats)


        self._save_data(self.output_path, data)
        self._save_statistics(self.stats_path, global_stats)
        self._send_to_mongodb(data, global_stats)
        print(f"Scoring complete. Results saved to {self.output_path} and {self.stats_path} and pushed to database.")

    def _load_data(self, path: str) -> list:
        """Loads the professor JSON data from disk."""
        abs_path = os.path.abspath(path)
        with open(abs_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        return [Professor(**d) if isinstance(d, dict) else d for d in raw_data]

    def _run_scoring(self, data: list) -> list:
        """Applies first and second round scoring engines to the data."""
        print("Scoring professors on first-round metrics...")
        factory = ScoringEngineFactory()
        data = factory.create_first_round_engine().process_data(data)
        data = factory.create_second_round_engine().process_data(data)
        print("Finished.")
        return data
    
    def _run_scoring_with_global_stats(self, data: list, global_stats) -> list:
        """Applies third round scoring engines to the data."""
        print("Scoring professors on second-round metrics...")
        factory = ScoringEngineFactory()
        data = factory.create_third_round_engine().process_data(data, global_stats)
        print("Finished.")
        return data
    
    def _calculate_statistics(self, data: list) -> GlobalStatistics:
        """Calculates global statistics from the scored professor data."""
        print("Performing global statistics calculations...")
        factory = ScoringEngineFactory()
        temp = factory.create_global_stat_engine().calculate_statistics(data)
        print("Finished.")
        return temp

    def _save_data(self, path: str, data: list) -> None:
        """Saves the processed professor data to JSON."""
        print("Saving scoring data...")
        with open(path, "w", encoding="utf-8") as f:
            json_data = [
                p.model_dump(by_alias=True) if isinstance(p, Professor) else p for p in data
            ]
            json.dump(json_data, f, indent=4)
        print("Finished.")
    
    def _send_to_mongodb(self, data: list, stats: GlobalStatistics) -> None:
        """Sends scoring data and global statistics to mongodb."""
        print("Sending data to mongodb cluster...")
        json_data = [
            p.model_dump(by_alias=True) if isinstance(p, Professor) else p for p in data
        ]
        stats_dict = stats.model_dump()
        
        uploader = MongoUploader()
        uploader.upload_professor_scores(json_data)
        uploader.upload_global_statistics(stats_dict)
        print("Finished.")


    def _save_statistics(self, path: str, stats: GlobalStatistics) -> None:
        """Saves the global statistics to JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stats.model_dump(), f, indent=4)
