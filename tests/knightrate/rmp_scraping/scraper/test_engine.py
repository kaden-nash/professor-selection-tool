import pytest
import json
from knightrate.rmp_scraping.scraper.engine import ScraperEngine
from knightrate.rmp_scraping.scraper.monitor import Monitor
from knightrate.rmp_scraping.scraper.storage import DataStorage

class MockClient:
    def __init__(self):
        self.call_count = 0
        
    def execute(self, query, vars, name):
        self.call_count += 1
        if name == "TeacherSearchPaginationQuery":
            if self.call_count > 1:
                return {"data":{"search":{"teachers":{"edges":[],"pageInfo":{"hasNextPage":False}, "resultCount":1}}}}
            return {
                "data":{
                    "search":{
                        "teachers":{
                            "edges":[
                                {"node":{"__typename":"Teacher","id":"T1","firstName":"A","lastName":"B","department":"CS", "numRatings":1, "avgDifficulty":1.1, "avgRating":1.1, "wouldTakeAgainPercent":50}}
                            ],
                            "pageInfo":{"hasNextPage":True, "endCursor":"C1"},
                            "resultCount":1
                        }
                    }
                }
            }
        else:
            return {
                "data":{
                    "node":{
                        "ratings":{
                            "edges":[
                                {"node":{"id":"R1", "clarityRating":5, "class":"101", "comment":"Great", "date":"2020", "difficultyRating":5, "helpfulRating":5, "isForCredit":True, "isForOnlineClass":False, "ratingTags":""}}
                            ], 
                            "pageInfo":{"hasNextPage":False}
                        }
                    }
                }
            }

def test_engine(tmp_path):
    storage_file = tmp_path / "test_data.json"
    storage = DataStorage(str(storage_file))
    monitor = Monitor()
    client = MockClient()
    
    engine = ScraperEngine(client, storage, monitor)
    engine.run()
    
    assert storage_file.exists()
    with open(storage_file, 'r') as f:
        data = json.load(f)
        
    assert data["metadata"]["resultCount"] == 1
    assert len(data["professors"]) == 1
    assert "reviews" in data["professors"][0]
    assert len(data["professors"][0]["reviews"]) == 1
    assert data["professors"][0]["reviews"][0]["id"] == "R1"
