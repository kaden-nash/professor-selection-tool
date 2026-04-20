from abc import ABC, abstractmethod
from typing import Any

class DataCorrelator(ABC):
    """
    Abstract base class for data correlators.
    """

    @abstractmethod
    def correlate(self, data1: Any, data2: Any) -> None:
        """Correlates two varied sources of data in memory."""
        pass

    @abstractmethod
    def get_correlated_data(self) -> Any:
        """Returns the final correlated dataset."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Saves the correlated data to the given filepath."""
        pass
