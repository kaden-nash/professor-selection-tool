from models import Professor, Scores, GlobalStatistics

class ScoringEngine:
    """Engine responsible for applying strategies to records."""

    def __init__(self):
        self.strategies = []
        self.statistic_strategies = []

    def register_strategy(self, strategy):
        """Adds a new scoring strategy to the engine."""
        self.strategies.append(strategy)

    def register_statistic(self, strategy):
        """Adds a new statistical strategy to the engine."""
        self.statistic_strategies.append(strategy)

    def process_data(self, data: list) -> list:
        """Processes a list of mixed data types, scoring Professor objects."""
        for i in range(len(data)):
            if isinstance(data[i], Professor):
                data[i] = self._score_professor(data[i]) 
        return data

    def _score_professor(self, professor: Professor) -> Professor:
        """Applies all strategies to a single professor."""
        if not professor.scores:
            professor.scores = Scores()
            
        for strategy in self.strategies:
            strategy_result = strategy.analyze(professor)
            current_scores = professor.scores.__dict__.copy()
            current_scores.update(strategy_result)
            professor.scores = Scores(**current_scores)
            
        return professor

    def calculate_statistics(self, data: list) -> GlobalStatistics:
        """Calculates global statistics from processed data."""
        stats_dict = {}
        professors = [p for p in data if isinstance(p, Professor)]
        
        for stat_strategy in self.statistic_strategies:
            stat_val = stat_strategy.calculate(professors)
            stats_dict[stat_strategy.metric_name] = stat_val
            
        return GlobalStatistics(**stats_dict)
