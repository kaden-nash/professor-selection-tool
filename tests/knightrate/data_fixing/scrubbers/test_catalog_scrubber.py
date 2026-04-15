import pytest
import json
from knightrate.data_fixing.scrubbers.catalog_scrubber import CatalogScrubber

@pytest.fixture
def dummy_catalog_file(tmp_path):
    p = tmp_path / "ucf_catalog.json"
    data = [
        "Abbas, Hadi, Professor of School of Visual Arts & Design (8/8/1995), M.F.A. (Wichita State University)",
        "SMITH, JOHN C.,Professor Emeritus",
        "O'Connor, Tim, Associate Professor of Physics (01/15/2010), Ph.D. (MIT)",
        "Invalid String Here",
        ""
    ]
    p.write_text(json.dumps(data))
    return p

def test_catalog_scrubber_behavior(dummy_catalog_file, tmp_path):
    scrubber = CatalogScrubber()
    scrubber.load(str(dummy_catalog_file))
    scrubber.scrub()
    
    data = scrubber.get_data()
    assert len(data) == 3
    
    # Standard 1
    assert data[0].last_name == "Abbas"
    assert data[0].first_name == "Hadi"
    assert data[0].role == "Professor"
    assert data[0].field_of_study == "School of Visual Arts & Design"
    assert data[0].date_joined_ucf == "1995-08-08"
    assert data[0].level_of_education == "M.F.A."
    assert data[0].graduated_from == "Wichita State University"
    assert not data[0].isEmeritus

    # Emeritus
    assert data[1].last_name == "Smith"
    assert data[1].first_name == "John C."
    assert data[1].role == "Professor Emeritus"
    assert data[1].isEmeritus

    # Standard 2 with apostrophe
    assert data[2].last_name == "O'Connor"
    assert data[2].first_name == "Tim"
    assert data[2].date_joined_ucf == "2010-01-15"
    assert data[2].graduated_from == "MIT"

    out_file = tmp_path / "catalog_cleaned.json"
    scrubber.save(str(out_file))
    
    saved_data = json.loads(out_file.read_text())
    assert len(saved_data) == 3
    assert saved_data[0]["lastName"] == "Abbas"
