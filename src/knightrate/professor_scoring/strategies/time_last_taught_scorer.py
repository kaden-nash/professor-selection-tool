from .base_strategy import ScoringStrategy
from ..models import Professor
import re

class TimeLastTaughtScorer(ScoringStrategy):

    def __init__(self):
        self.metric_name = "timeLastTaught"

    def analyze(self, professor: Professor) -> dict:
        date = self._get_month_and_year(professor)

        if date == "Unknown":
            return {self.metric_name: date}

        time = self._get_time_last_taught(date) # type: ignore
        return {self.metric_name: time}
    
    def _get_month_and_year(self, professor: Professor) -> dict[str, int] | str:
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
        # summer: between june and august [6-8]
        # fall: between september and january [9-1]
        # spinrg: between february and may [2-5]
        time = ""
        if date.get("month", 0) >= 6 and date.get("month", 0) <= 8:
            time = "Summer " + str(date.get("year", 0))
        elif date.get("month", 0) >= 2 and date.get("month", 0) <= 5:
            time = "Spring " + str(date.get("year", 0))
        else:
            time = "Fall " + str(date.get("year", 0))
        return time
        
        
