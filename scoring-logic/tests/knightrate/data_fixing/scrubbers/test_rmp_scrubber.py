import pytest
import json
from src.knightrate.data_fixing.scrubbers.rmp_scrubber import RmpScrubber

@pytest.fixture
def dummy_rmp_file(tmp_path):
    p = tmp_path / "rmp_data.json"
    data = {
        "professors": [
            {
                "id": "1",
                "reviews": [
                    {"class": "COP4331"},
                    {"class": "CHM2210H"},
                    {"class": "CHM2210K"},
                    {"class": "CHM2210L"},
                    {"class": "CHM2210C"},
                    {"class": "MAC2311X"},
                    {"class": "EG3310"},
                    {"class": "VARIOUS"},
                    {"class": ""},
                    {"class": "COP 4331"},
                    {"class": "cop3502"},
                    {"class": "COP-3502"},
                    {"class": "cop-3502-"},
                    {"class": "CDA5106"}
                ]
            }
        ]
    }
    p.write_text(json.dumps(data))
    return p

def test_rmp_scrubber_behavior(dummy_rmp_file, tmp_path):
    scrubber = RmpScrubber()
    scrubber.load(str(dummy_rmp_file))
    scrubber.scrub()
    
    data = scrubber.get_data()
    assert len(data) == 1
    reviews = data[0].get("reviews", [])
    assert len(reviews) == 14
    
    assert reviews[0]["class"] == "COP4331"
    assert reviews[1]["class"] == "CHM2210H"
    assert reviews[2]["class"] == "CHM2210H"
    assert reviews[3]["class"] == "CHM2210"
    assert reviews[4]["class"] == "CHM2210"
    assert reviews[5]["class"] == "unknown"  # X is unmatched letter
    assert reviews[6]["class"] == "unknown"  # 2-letters should be unknown
    assert reviews[7]["class"] == "unknown"  # VARIOUS -> unknown
    assert reviews[8]["class"] == "unknown"  # empty -> unknown
    assert reviews[9]["class"] == "COP4331"  # space stripped -> valid
    assert reviews[10]["class"] == "COP3502" # lowercase converted -> valid
    assert reviews[11]["class"] == "COP3502" # internal dash stripped -> valid
    assert reviews[12]["class"] == "COP3502" # multiple dashes stripped -> valid
    assert reviews[13]["class"] == "CDA5106" # grad course formatting holds
    
    out_file = tmp_path / "rmp_cleaned.json"
    scrubber.save(str(out_file))
    
    saved_data = json.loads(out_file.read_text())
    assert len(saved_data) == 1
    assert saved_data[0]["reviews"][1]["class"] == "CHM2210H"
