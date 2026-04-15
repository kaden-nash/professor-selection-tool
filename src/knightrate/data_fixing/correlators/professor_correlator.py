import json
from datetime import datetime
from typing import Any, List, Dict, Optional, Set
from ..core.correlator_interface import DataCorrelator
from ..models.models import CatalogProfessor, UnifiedProfessor, Course

class ProfessorCorrelator(DataCorrelator):
    """
    Correlates RMP professor data with Catalog professor data by name.
    Handles duplicate names by correlating earliest start date with earliest review date.
    """

    def __init__(self) -> None:
        self.unified_data: List[UnifiedProfessor] = []
        self.valid_courses: Dict[str, Course] = {}

    def correlate(self, rmp_data: List[Dict[str, Any]], catalog_data: List[CatalogProfessor], courses_data: Optional[List[Course]] = None) -> None:
        if courses_data:
            self.valid_courses = {f"{c.course_code}{c.course_number}": c for c in courses_data}
            
        cat_by_name = self._group_catalog_by_name(catalog_data)
        rmp_by_name = self._group_rmp_by_name(rmp_data)
        self.unified_data = []

        for name_key, rmp_list in rmp_by_name.items():
            cat_list = cat_by_name.get(name_key, [])
            self._correlate_name_group(rmp_list, cat_list)

        self.unified_data = [
            up for up in self.unified_data
            if up.rmp_data.get("numRatings", 0) >= 5 and self._has_recent_reviews(up)
        ]

    def _group_catalog_by_name(self, catalog: List[CatalogProfessor]) -> Dict[str, List[CatalogProfessor]]:
        grouped: Dict[str, List[CatalogProfessor]] = {}
        for cp in catalog:
            key = f"{cp.first_name} {cp.last_name}".lower()
            grouped.setdefault(key, []).append(cp)
        return grouped

    def _group_rmp_by_name(self, rmp: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for rp in rmp:
            first = rp.get("firstName", "")
            last = rp.get("lastName", "")
            key = f"{first} {last}".lower()
            grouped.setdefault(key, []).append(rp)
        return grouped

    def _correlate_name_group(self, rmp_list: List[Dict[str, Any]], cat_list: List[CatalogProfessor]) -> None:
        cat_sorted = sorted(cat_list, key=self._get_catalog_start_date)
        rmp_sorted = sorted(rmp_list, key=self._get_rmp_first_review_date)
        
        for idx, rmp_prof in enumerate(rmp_sorted):
            cat_prof = cat_sorted[idx] if idx < len(cat_sorted) else None
            self._process_single_match(rmp_prof, cat_prof)

    def _process_single_match(self, rmp_prof: Dict[str, Any], cat_prof: Optional[CatalogProfessor]) -> None:
        unified = UnifiedProfessor(rmp_data=rmp_prof)
        if cat_prof:
            unified.merge_catalog_data(cat_prof)
            
        self._extract_courses(unified)
        self.unified_data.append(unified)

    def _extract_courses(self, unified: UnifiedProfessor) -> None:
        reviews = unified.rmp_data.get("reviews", [])
        courses_set = set()
        for r in reviews:
            c = r.get("class", "")
            if c and c != "unknown":
                if not self.valid_courses:
                    courses_set.add(c)
                else:
                    if c in self.valid_courses:
                        courses_set.add(c)
                    elif c.endswith('H'):
                        base_c = c[:-1]
                        if base_c in self.valid_courses and self.valid_courses[base_c].hasHonorsVersion:
                            courses_set.add(c)
                    elif len(c) >= 4 and c[3] in ('5', '6', '7', '8'):
                        courses_set.add(c)
        unified.courses_taught = sorted(list(courses_set))

    def _get_catalog_start_date(self, cp: CatalogProfessor) -> datetime:
        dt_str = cp.date_joined_ucf
        if not dt_str:
            return datetime.max
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d")
        except ValueError:
            return datetime.max

    def _get_rmp_first_review_date(self, rp: Dict[str, Any]) -> datetime:
        first_date = self._parse_explicit_first_date(rp)
        if first_date:
            return first_date
            
        return self._find_earliest_rating_date(rp)

    def _parse_explicit_first_date(self, rp: Dict[str, Any]) -> Optional[datetime]:
        if "firstReviewDate" in rp:
            try:
                return datetime.strptime(rp["firstReviewDate"], "%Y-%m-%d")
            except ValueError:
                return None
        return None

    def _find_earliest_rating_date(self, rp: Dict[str, Any]) -> datetime:
        reviews = rp.get("reviews", [])
        if not reviews or not isinstance(reviews, list):
            return datetime.max
            
        earliest = datetime.max
        for r in reviews:
            earliest = self._get_minimum_date(earliest, r.get("date", ""))
                
        return earliest

    def _parse_date_str(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            clean_date = date_str.replace(" UTC", "").replace(" +0000", "")
            clean_date = clean_date.replace("T", " ").replace("Z", "")
            if len(clean_date) > 19:
                clean_date = clean_date[:19]
            return datetime.strptime(clean_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    def _get_minimum_date(self, current_earliest: datetime, date_str: str) -> datetime:
        dt = self._parse_date_str(date_str)
        if dt and dt < current_earliest:
            return dt
        return current_earliest

    def _has_recent_reviews(self, up: UnifiedProfessor) -> bool:
        reviews = up.rmp_data.get("reviews", [])
        if not reviews:
            return True
            
        cutoff = datetime(2016, 6, 1)
        for r in reviews:
            dt = self._parse_date_str(r.get("date", ""))
            if dt and dt >= cutoff:
                return True
                
        return False

    def save(self, filepath: str) -> None:
        out_data = [u.to_dict() for u in self.unified_data]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(out_data, f, indent=4)

    def get_correlated_data(self) -> List[UnifiedProfessor]:
        return self.unified_data
