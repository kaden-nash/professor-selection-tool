import json
import re
from typing import List, Optional
from data_fixing.core.scrubber_interface import DataScrubber
from data_fixing.models.models import Course

class CourseScrubber(DataScrubber):
    def __init__(self) -> None:
        self.raw_data: List[str] = []
        self.scrubbed_data: List[Course] = []

    def load(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

    def scrub(self) -> None:
        self.scrubbed_data = []
        data_list = self.raw_data.get("courses", []) if isinstance(self.raw_data, dict) else self.raw_data
        for course_str in data_list:
            course_obj = self._parse_course_string(course_str)
            if course_obj:
                self.scrubbed_data.append(course_obj)

    def _parse_course_string(self, course_str: str) -> Optional[Course]:
        EXPECTED_PARTS = 2
        parts = course_str.split(" - ", 1)
        if len(parts) != EXPECTED_PARTS:
            return None
            
        full_code, course_name = parts
        return self._extract_code_and_build(full_code.strip(), course_name.strip())

    def _extract_code_and_build(self, full_code: str, course_name: str) -> Optional[Course]:
        code_match = re.match(r'^([A-Z]+)(\d+[A-Z]*)$', full_code, re.IGNORECASE)
        
        if not code_match:
            return None
            
        CODE_GROUP = 1
        NUM_GROUP = 2
        course_code = code_match.group(CODE_GROUP).upper()
        raw_number_str = code_match.group(NUM_GROUP).upper()
        
        return self._build_course(course_code, raw_number_str, course_name)

    def _build_course(self, code: str, num_str: str, name: str) -> Course:
        has_honors = False
        has_lab = False
        final_num = num_str

        if not num_str[-1].isdigit():
            last_char = num_str[-1]
            if last_char in ['H', 'K']:
                has_honors = True
            elif last_char == 'L':
                has_lab = True
            
            # Remove any trailing letter (slice from start to len-1)
            final_num = num_str[:-1]

        return Course(
            course_code=code,
            course_number=final_num,
            course_name=name,
            hasHonorsVersion=has_honors,
            hasLab=has_lab
        )

    def save(self, filepath: str) -> None:
        output_data = [c.to_dict() for c in self.scrubbed_data]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4)

    def get_data(self) -> List[Course]:
        return self.scrubbed_data
