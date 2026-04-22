from src.knightrate.data_fixing.core.scrubber_interface import DataScrubber
from src.knightrate.data_fixing.core.correlator_interface import DataCorrelator
from typing import Any

class DummyScrubber(DataScrubber):
    def load(self, filepath: str) -> None:
        super().load(filepath)
    def scrub(self) -> None:
        super().scrub()
    def save(self, filepath: str) -> None:
        super().save(filepath)
    def get_data(self) -> Any:
        super().get_data()

class DummyCorrelator(DataCorrelator):
    def correlate(self, data1: Any, data2: Any) -> None:
        super().correlate(data1, data2)
    def get_correlated_data(self) -> Any:
        super().get_correlated_data()
    def save(self, filepath: str) -> None:
        super().save(filepath)

def test_interfaces():
    # Calling these on abstract classes directly isn't possible, 
    # but through subclasses we can verify they hit `pass` safely
    s = DummyScrubber()
    s.load("")
    s.scrub()
    s.save("")
    s.get_data()
    
    c = DummyCorrelator()
    c.correlate(None, None)
    c.get_correlated_data()
    c.save("")
