import json
import os
from .engine.engine_factory import ScoringEngineFactory
from .models import Professor, GlobalStatistics

def main():
    """Main execution entry point."""
    input_path = "../data_fixing/professor_data.json"
    output_path = "professor_ratings.json"
    
    data = load_data(input_path)
    factory = ScoringEngineFactory()
    engine = factory.create_first_round_engine()
    processed_data = engine.process_data(data)
    engine = factory.create_second_round_engine()
    processed_data = engine.process_data(processed_data)
    engine = factory.create_global_stat_engine()
    stats_output_path = "global_statistics.json"
    global_stats = engine.calculate_statistics(processed_data)
    
    save_data(output_path, processed_data)
    save_statistics(stats_output_path, global_stats)
    print(f"Scoring complete. Results saved to {output_path} and {stats_output_path}")

def load_data(path: str) -> list:
    """Loads the professor JSON data."""
    abs_path = os.path.abspath(path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        return [Professor(**d) if isinstance(d, dict) else d for d in raw_data]

def save_data(path: str, data: list) -> None:
    """Saves the processed data back to JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json_data = [p.model_dump(by_alias=True) if isinstance(p, Professor) else p for p in data]
        json.dump(json_data, f, indent=4)

def save_statistics(path: str, stats: GlobalStatistics) -> None:
    """Saves the global statistics to JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(stats.model_dump(), f, indent=4)

if __name__ == "__main__":
    main()
