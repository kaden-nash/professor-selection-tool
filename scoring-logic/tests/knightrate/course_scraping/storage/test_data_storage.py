import os
import json
import pytest
from knightrate.course_scraping.storage.data_storage import DataStorage

def test_save_courses_creates_file(tmp_path):
    storage = DataStorage(directory=str(tmp_path))
    courses = ["COP3502C - Computer Science I"]
    
    storage.save_courses(courses)
    
    filepath = tmp_path / "courses.json"
    assert filepath.exists()
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "courses" in data
    assert data["courses"] == courses

def test_save_courses_empty_list_does_not_save(tmp_path):
    storage = DataStorage(directory=str(tmp_path))
    courses = []
    
    storage.save_courses(courses)
    
    filepath = tmp_path / "courses.json"
    assert not filepath.exists()

def test_save_courses_custom_filename(tmp_path):
    storage = DataStorage(directory=str(tmp_path))
    courses = ["ADE4382 - Teaching Adult Learners in Technical Programs"]
    
    storage.save_courses(courses, filename="custom.json")
    
    filepath = tmp_path / "custom.json"
    assert filepath.exists()
