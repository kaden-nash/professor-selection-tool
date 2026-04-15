from abc import ABC, abstractmethod
from typing import Any

class DataScrubber(ABC):
    """
    Abstract base class for all data scrubbers.
    Ensures a consistent interface.
    """

    @abstractmethod
    def load(self, filepath: str) -> None:
        """Loads data from the given filepath into memory."""
        pass

    @abstractmethod
    def scrub(self) -> None:
        """Performs scrubbing operations on the loaded data."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Saves the scrubbed data to the given filepath."""
        pass

    @abstractmethod
    def get_data(self) -> Any:
        """Returns the scrubbed data."""
        pass
