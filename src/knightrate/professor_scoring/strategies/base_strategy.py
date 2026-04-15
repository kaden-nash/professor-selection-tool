from abc import ABC, abstractmethod
from ..models import Professor

class ScoringStrategy(ABC):
    """Abstract base class for all professor scoring strategies."""

    @abstractmethod
    def analyze(self, professor: Professor) -> dict:
        """
        Calculates a score for the given professor.
        
        Args:
            professor (Professor): The professor data object.
            
        Returns:
            dict: A string to float dictionary mapping metric to score.
        """
        pass  # pragma: no cover
