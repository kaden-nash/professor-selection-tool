import json
import re
from typing import Any, List, Dict
from data_fixing.core.scrubber_interface import DataScrubber

class RmpScrubber(DataScrubber):
    def __init__(self) -> None:
        self.raw_data: List[Dict[str, Any]] = []
        self.scrubbed_data: List[Dict[str, Any]] = []

    def load(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

    def scrub(self) -> None:
        self.scrubbed_data = []
        prof_list = self.raw_data.get("professors", []) if isinstance(self.raw_data, dict) else self.raw_data
        for prof in prof_list:
            new_prof = prof.copy()
            reviews = new_prof.get("reviews", [])
            scrubbed_reviews = [self._scrub_review(r) for r in reviews]
            new_prof["reviews"] = scrubbed_reviews
            self.scrubbed_data.append(new_prof)

    def _scrub_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        new_review = review.copy()
        
        class_str = new_review.get("class", "").strip().upper()
        if not class_str:
            new_review["class"] = "unknown"
            return new_review
            
        new_review["class"] = self._cleanup_class_string(class_str)
        return new_review

    def _cleanup_class_string(self, class_str: str) -> str:
        class_str = re.sub(r'[^A-Za-z0-9]', '', class_str).upper()
        base_match = re.match(r'^([A-Z]{3})(\d{4})$', class_str)
        if base_match:
            return class_str
            
        trailing_match = re.match(r'^([A-Z]{3})(\d{4})([A-Z])$', class_str)
        if trailing_match:
            CODE_GROUP = 1
            NUM_GROUP = 2
            LETTER_GROUP = 3
            letter = trailing_match.group(LETTER_GROUP)
            if letter == 'H':
                return class_str
            elif letter == 'K':
                return trailing_match.group(CODE_GROUP) + trailing_match.group(NUM_GROUP) + 'H'
            elif letter in ('L', 'C'):
                return trailing_match.group(CODE_GROUP) + trailing_match.group(NUM_GROUP)
            
        return "unknown"

    def save(self, filepath: str) -> None:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scrubbed_data, f, indent=4)

    def get_data(self) -> List[Dict[str, Any]]:
        return self.scrubbed_data
