from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path

class DataScrubber(ABC):
    """
    Abstract base class for all data scrubbers.
    """

    @abstractmethod
    def load(self, filepath: Path) -> None:
        """Loads data from the given filepath into memory."""
        pass

    @abstractmethod
    def scrub(self) -> None:
        """Performs scrubbing operations on the loaded data."""
        pass

    @abstractmethod
    def save(self, filepath: Path) -> None:
        """Saves the scrubbed data to the given filepath."""
        pass

    @abstractmethod
    def get_data(self) -> Any:
        """Returns the scrubbed data."""
        pass
