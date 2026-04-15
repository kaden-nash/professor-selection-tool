from abc import ABC, abstractmethod
from typing import List
from ..models import Professor

class StatisticStrategy(ABC):
    """Abstract base class for all global statistics calculators."""

    @abstractmethod
    def calculate(self, professors: List[Professor]) -> float:
        """
        Runs analytical statistics across the entire pool of scored professors.
        
        Args:
            professors (List[Professor]): The scored professors.
            
        Returns:
            float: Extracted dataset statistics properties.
        """
        pass  # pragma: no cover
