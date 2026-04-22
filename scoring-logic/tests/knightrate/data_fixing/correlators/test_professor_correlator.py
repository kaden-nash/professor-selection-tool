import pytest
import json
from src.knightrate.data_fixing.models.models import CatalogProfessor, Course
from src.knightrate.data_fixing.correlators.professor_correlator import ProfessorCorrelator

def test_professor_correlator(tmp_path):
    rmp_data = [
        # Match 1: 1:1 match
        {"firstName": "Hadi", "lastName": "Abbas", "avgRating": 4.5, "reviews": [], "numRatings": 10},
        
        # Match 2: Duplicate Resolution
        # We simulate two "John Smith"s in RMP and two in Catalog.
        {"firstName": "John", "lastName": "Smith", "id": "1", "firstReviewDate": "2020-01-01", "numRatings": 10},
        {"firstName": "John", "lastName": "Smith", "id": "2", "firstReviewDate": "2015-05-05", "numRatings": 10},
        
        # Match 3: No Catalog match
        {
            "firstName": "Unknown", "lastName": "Professor", "avgRating": 1.0, "numRatings": 10,
            "reviews": [{"class": "CHM2210H", "date": "2022-12-06 05:34:18 +0000 UTC"}]
        },
        
        # Match 4: Date edge cases (ratings list and bad dates)
        {
            "firstName": "Bad", "lastName": "Date", "id": "b1",
            "firstReviewDate": "invalid-format",
            "numRatings": 10,
            "reviews": [{"date": "2023-01-01T12:00:00Z"}, {"date": "invalid"}, {"date": "2022-01-01T12:00:00Z"}, {"nodate": True}]
        },
        {
            "firstName": "Bad", "lastName": "Date", "id": "b2", "numRatings": 10
            # No dates here at all, should use datetime.max
        },
        
        # Match 5: Less than 5 reviews omitted
        {
             "firstName": "Ignored", "lastName": "Professor", "numRatings": 4
        },
        
        # Match 6: Honors course validation
        {
             "firstName": "Honors", "lastName": "Teacher", "numRatings": 10,
             "reviews": [{"class": "CHM2210H", "date": "2020-01-01T12:00:00Z"}, {"class": "MAC2311H", "date": "2020-01-01T12:00:00Z"}]
        },
        
        # Match 7: Pre-2016 activity validation (should prune)
        {
             "firstName": "Old", "lastName": "Timer", "numRatings": 10,
             "reviews": [{"class": "COP3502", "date": "2015-05-06 05:34:18 +0000 UTC"}, {"class": "COP3502", "date": "2012-12-06 05:34:18 +0000 UTC"}]
        }
    ]

    catalog_data = [
        CatalogProfessor(
            last_name="Abbas",
            first_name="Hadi",
            role="Professor",
            field_of_study="Art",
            date_joined_ucf="1995-08-08",
            level_of_education="MFA",
            graduated_from="Wichita",
            isEmeritus=False
        ),
        # John Smith 1 (Start 2018)
        CatalogProfessor(
            last_name="Smith",
            first_name="John",
            role="Assistant Prof",
            field_of_study="Math",
            date_joined_ucf="2018-01-01",
            level_of_education="PhD",
            graduated_from="MIT"
        ),
        # John Smith 2 (Start 2012)
        CatalogProfessor(
            last_name="Smith",
            first_name="John",
            role="Associate Prof",
            field_of_study="Math",
            date_joined_ucf="2012-05-05",
            level_of_education="PhD",
            graduated_from="MIT"
        ),
        CatalogProfessor(
            last_name="Date",
            first_name="Bad",
            role="Professor",
            field_of_study="Time",
            date_joined_ucf="invalid-date",
            level_of_education="BS",
            graduated_from="Time University",
            isEmeritus=False
        ),
        CatalogProfessor(
            last_name="Date",
            first_name="Bad",
            role="Associate",
            field_of_study="Time",
            date_joined_ucf="", # empty date
            level_of_education="BA",
            graduated_from="Time College",
            isEmeritus=False
        )
    ]

    courses_data = [
        Course(course_code="CHM", course_number="2210", course_name="Chemistry", hasHonorsVersion=True),
        Course(course_code="MAC", course_number="2311", course_name="Calculus", hasHonorsVersion=False)
    ]

    correlator = ProfessorCorrelator()
    correlator.correlate(rmp_data, catalog_data, courses_data)
    
    results = correlator.get_correlated_data()
    assert len(results) == 7  # 6 old elements + Honors Teacher. Ignored Professor logic pruned 1.
    
    # Let's map by a unique RMP trait to verify correlation
    # We should have one Hadi Abbas
    hadi = [r for r in results if r.rmp_data.get("firstName") == "Hadi"][0]
    assert hadi.catalog_data is not None
    assert hadi.to_dict()["role"] == "Professor"
    
    # We should have one Unknown Professor with no catalog data
    unk = [r for r in results if r.rmp_data.get("firstName") == "Unknown"][0]
    assert unk.catalog_data is None
    assert unk.to_dict().get("role") is None
    assert "CHM2210H" in unk.courses_taught
    
    # John Smith resolution:
    # RMP 2 (id=2) has firstReview 2015. RMP 1 (id=1) has 2020.
    # Cat 2 has start 2012. Cat 1 has start 2018.
    # They sort order: 
    # RMP: id=2 (2015), id=1 (2020)
    # Cat: 2012, 2018
    # Map: id=2 -> 2012, id=1 -> 2018
    johns = [r for r in results if r.rmp_data.get("firstName") == "John"]
    assert len(johns) == 2
    
    john_id_2 = [j for j in johns if j.rmp_data.get("id") == "2"][0]
    assert john_id_2.catalog_data is not None
    assert john_id_2.catalog_data.date_joined_ucf == "2012-05-05"
    
    john_id_1 = [j for j in johns if j.rmp_data.get("id") == "1"][0]
    assert john_id_1.catalog_data is not None
    assert john_id_1.catalog_data.date_joined_ucf == "2018-01-01"
    
    # Bad dates logic verification
    bads = [r for r in results if r.rmp_data.get("firstName") == "Bad"]
    assert len(bads) == 2
    # sorting maxes out invalid dates, so order is just whatever sorted order is.
    
    # Ignored test (sub-5 reviews prune validation)
    ignored = [r for r in results if r.rmp_data.get("firstName") == "Ignored"]
    assert len(ignored) == 0

    # Old Timer test (pre-2016 reviews prune validation)
    old = [r for r in results if r.rmp_data.get("firstName") == "Old"]
    assert len(old) == 0

    # Honors validation verification
    honors_teacher = [r for r in results if r.rmp_data.get("firstName") == "Honors"][0]
    assert "CHM2210H" in honors_teacher.courses_taught
    assert "MAC2311H" not in honors_teacher.courses_taught

    out_file = tmp_path / "professor_data.json"
    correlator.save(str(out_file))
    saved_data = json.loads(out_file.read_text())
    assert len(saved_data) == 7
