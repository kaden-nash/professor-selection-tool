import pytest
import os
import json
from src.knightrate.data_fixing.scrubbers.course_scrubber import CourseScrubber

@pytest.fixture
def dummy_courses_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "courses.json"
    data = [
        "ADE4382 - Teaching Adult Learners in Technical Programs",
        "COP4331C - Processes for Object Oriented Software Development",
        "MAC2311H - Calculus I Honors",
        "CHM2045L - Chemistry Lab",
        "INVALID_STRING",
        "XYZ - Just a Name"
    ]
    p.write_text(json.dumps(data))
    return p

def test_course_scrubber_load_scrub_save(dummy_courses_file, tmp_path):
    scrubber = CourseScrubber()
    scrubber.load(str(dummy_courses_file))
    scrubber.scrub()
    
    data = scrubber.get_data()
    assert len(data) == 4
    
    # ADE4382
    assert data[0].course_code == "ADE"
    assert data[0].course_number == "4382"
    assert not data[0].hasHonorsVersion
    assert not data[0].hasLab
    
    # COP4331C
    assert data[1].course_code == "COP"
    assert data[1].course_number == "4331"
    assert not data[1].hasHonorsVersion
    assert not data[1].hasLab
    
    # MAC2311H
    assert data[2].course_code == "MAC"
    assert data[2].course_number == "2311"
    assert data[2].hasHonorsVersion
    assert not data[2].hasLab
    
    # CHM2045L
    assert data[3].course_code == "CHM"
    assert data[3].course_number == "2045"
    assert not data[3].hasHonorsVersion
    assert data[3].hasLab
    
    out_file = tmp_path / "courses_cleaned.json"
    scrubber.save(str(out_file))
    
    saved_data = json.loads(out_file.read_text())
    assert len(saved_data) == 4
    assert saved_data[0]["courseCode"] == "ADE"
