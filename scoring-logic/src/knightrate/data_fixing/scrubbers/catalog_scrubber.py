import json
import re
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

from ..core.scrubber_interface import DataScrubber
from ..models.models import CatalogProfessor

class CatalogScrubber(DataScrubber):
    def __init__(self) -> None:
        self.raw_data: List[str] = []
        self.scrubbed_data: List[CatalogProfessor] = []

    def load(self, filepath: str | Path) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

    def scrub(self) -> None:
        self.scrubbed_data = []
        data_list = self.raw_data.get("professors", []) if isinstance(self.raw_data, dict) else self.raw_data
        for prof_str in data_list:
            prof_str_clean = prof_str.strip()
            if not prof_str_clean:
                continue
                
            prof_obj = self._parse_professor_string(prof_str_clean)
            if prof_obj:
                self.scrubbed_data.append(prof_obj)

    def _parse_professor_string(self, prof_str: str) -> Optional[CatalogProfessor]:
        if "Emeritus" in prof_str:
            return self._parse_emeritus(prof_str)
        else:
            return self._parse_standard(prof_str)

    def _parse_emeritus(self, prof_str: str) -> CatalogProfessor:
        parts = prof_str.split(",")
        LAST_NAME_INDEX = 0
        FIRST_NAME_INDEX = 1
        last_name = parts[LAST_NAME_INDEX].strip().title()
        first_name = parts[FIRST_NAME_INDEX].strip().title()
        
        return CatalogProfessor(
            last_name=last_name,
            first_name=first_name,
            role="Professor Emeritus",
            field_of_study="",
            date_joined_ucf="",
            level_of_education="",
            graduated_from="",
            isEmeritus=True
        )

    def _parse_standard(self, prof_str: str) -> Optional[CatalogProfessor]:
        EXPECTED_PARTS = 3
        parts = prof_str.split(",", 2)
        if len(parts) < EXPECTED_PARTS:
            return None
            
        last_name, first_name, remaining = parts
        return self._extract_standard_details(last_name.strip(), first_name.strip(), remaining.strip())

    def _extract_standard_details(self, last: str, first: str, details: str) -> CatalogProfessor:
        role, field_of_study = self._parse_role_and_field(details)
        date_joined = self._parse_date_joined(details)
        level_edu, grad_from = self._parse_education(details)
        
        return CatalogProfessor(
            last_name=last.title(),
            first_name=first.title(),
            role=role,
            field_of_study=field_of_study,
            date_joined_ucf=date_joined,
            level_of_education=level_edu,
            graduated_from=grad_from,
            isEmeritus=False
        )

    def _parse_role_and_field(self, details: str) -> Tuple[str, str]:
        parts = details.split(" of ", 1)
        ROLE_INDEX = 0
        role = parts[ROLE_INDEX].strip()
        field = ""
        if len(parts) > 1:
            FIELD_INFO_INDEX = 1
            field_part = parts[FIELD_INFO_INDEX].split("(")[0]
            field = field_part.strip()
        return role, field

    def _parse_date_joined(self, details: str) -> str:
        match = re.search(r'\(([\d/]+)\)', details)
        if match:
            DATE_GROUP = 1
            date_str = match.group(DATE_GROUP)
            try:
                dt = datetime.strptime(date_str, "%m/%d/%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return date_str
        return ""

    def _parse_education(self, details: str) -> Tuple[str, str]:
        edu_part = ""
        if "), " in details:
            edu_part = details.split("), ")[-1]
        
        level = edu_part
        grad_from = ""
        
        match = re.search(r'(.*?)\((.*?)\)', edu_part)
        if match:
            LEVEL_GROUP = 1
            GRAD_GROUP = 2
            level = match.group(LEVEL_GROUP).strip()
            grad_from = match.group(GRAD_GROUP).strip()
        
        return level, grad_from

    def save(self, filepath: str | Path) -> None:
        out_data = [p.to_dict() for p in self.scrubbed_data]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(out_data, f, indent=4)

    def get_data(self) -> List[CatalogProfessor]:
        return self.scrubbed_data
