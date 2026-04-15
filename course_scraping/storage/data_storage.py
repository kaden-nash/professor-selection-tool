import json
import os

class DataStorage:
    """Handles saving parsed course data to persistent JSON storage."""

    def __init__(self, directory: str = "."):
        self.directory = directory

    def save_courses(self, courses: list[str], filename: str = "courses.json") -> None:
        """Saves a list of course titles to a JSON file."""
        if not courses:
            return

        filepath = os.path.join(self.directory, filename)
        data = {"courses": courses}

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
