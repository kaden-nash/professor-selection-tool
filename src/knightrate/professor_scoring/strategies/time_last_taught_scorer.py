from .base_strategy import ScoringStrategy
from ..models import Professor
import re

class TimeLastTaughtScorer(ScoringStrategy):
    """Determines the last time a professor taught based on their most recent reviews and the course catalog."""

    def __init__(self):
        self.metric_name = "timeLastTaught"

    def analyze(self, professor: Professor) -> dict:
        date = self._get_month_and_year(professor)

        if date == "Unknown":
            return {self.metric_name: date}

        time = self._get_time_last_taught(date) # type: ignore
        return {self.metric_name: time}
    
    def _get_month_and_year(self, professor: Professor) -> dict[str, int] | str:
        """Gets the month and year from a review's date string."""
        if not professor.reviews:
            return "Unknown"
        most_recent_review = professor.reviews[0]
        match = re.match(r"^(\d{4})-(\d{2})", most_recent_review.date)

        if not match:
            return "Unknown"

        year = int(match.group(1))   # "2012"
        month = int(match.group(2))  # "07"
        return {"year": year, "month": month}

    def _get_time_last_taught(self, date: dict[str, int]):
        """Categorizes the time last taught into Summer, Spring, or Fall"""
        time = ""
        FEBRUARY = 2
        MAY = 5
        JUNE = 6
        AUGUST = 8
        if date.get("month", 0) >= JUNE and date.get("month", 0) <= AUGUST:
            time = "Summer " + str(date.get("year", 0))
        elif date.get("month", 0) >= FEBRUARY and date.get("month", 0) <= MAY:
            time = "Spring " + str(date.get("year", 0))
        else:
            time = "Fall " + str(date.get("year", 0))
        return time
        
        
