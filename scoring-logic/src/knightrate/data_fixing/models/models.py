from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class Course:
    "Represents a course from the UCF course catalog."
    course_code: str
    course_number: str
    course_name: str
    hasHonorsVersion: bool = False
    hasLab: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "courseCode": self.course_code,
            "courseNumber": self.course_number,
            "courseName": self.course_name,
            "hasHonorsVersion": self.hasHonorsVersion,
            "hasLab": self.hasLab
        }

@dataclass
class CatalogProfessor:
    "Represents a professor from the UCF course catalog."
    last_name: str
    first_name: str
    role: str
    field_of_study: str
    date_joined_ucf: str
    level_of_education: str
    graduated_from: str
    isEmeritus: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "firstName": self.first_name,
            "lastName": self.last_name,
            "role": self.role,
            "fieldOfStudy": self.field_of_study,
            "dateJoinedUcf": self.date_joined_ucf,
            "levelOfEducation": self.level_of_education,
            "graduatedFrom": self.graduated_from,
            "isEmeritus": self.isEmeritus
        }

@dataclass
class UnifiedProfessor:
    """
    Represents a unified professor, containing logic to merge RMP data 
    and Catalog data together.
    """
    rmp_data: Dict[str, Any]
    catalog_data: Optional[CatalogProfessor] = None
    courses_taught: List[str] = field(default_factory=list)

    def merge_catalog_data(self, catalog_prof: CatalogProfessor) -> None:
        self.catalog_data = catalog_prof

    def to_dict(self) -> Dict[str, Any]:
        result = self.rmp_data.copy()
        if self.catalog_data:
            cat_dict = self.catalog_data.to_dict()
            result.update(cat_dict)
        result["courses_taught"] = self.courses_taught
        return result
