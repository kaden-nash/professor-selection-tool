import pytest
from knightrate.rmp_scraping.scraper.parser import parse_professors, parse_ratings

MOCK_PROFESSOR_DATA = {"data":{"search":{"teachers":{"didFallback":False,"edges":[{"cursor":"YXJyYXljb25uZWN0aW9uOjIw","node":{"__typename":"Teacher","avgDifficulty":4.2,"avgRating":1.1,"department":"Engineering","firstName":"Aaron","id":"VGVhY2hlci0zMTE4NDM2","isSaved":False,"lastName":"Hoskins","legacyId":3118436,"numRatings":62,"school":{"id":"U2Nob29sLTEwODI=","name":"University of Central Florida"},"wouldTakeAgainPercent":3.2258}}],"pageInfo":{"endCursor":"YXJyYXljb25uZWN0aW9uOjI0","hasNextPage":True},"resultCount":6340}}}}

MOCK_RATINGS_DATA = {"data":{"node":{"__typename":"Teacher","firstName":"Tanvir","id":"VGVhY2hlci0yNDU1MTI0","isProfCurrentUser":False,"lastName":"Ahmed","legacyId":2455124,"lockStatus":"none","numRatings":374,"ratings":{"edges":[{"cursor":"YXJyYXljb25uZWN0aW9uOjU=","node":{"__typename":"Rating","adminReviewedAt":"2025-12-12 15:34:43 +0000 UTC","attendanceMandatory":"non mandatory","clarityRating":5,"class":"COP3223C","comment":"Ahmed was a great choice.","createdByUser":False,"date":"2025-12-12 15:34:23 +0000 UTC","difficultyRating":4,"flagStatus":"UNFLAGGED","grade":"A","helpfulRating":5,"id":"UmF0aW5nLTQyMjA2MzAx","isForCredit":True,"isForOnlineClass":False,"legacyId":42206301,"ratingTags":"Accessible outside class--Lots of homework","teacherNote":None,"textbookUse":-1,"thumbs":[],"thumbsDownTotal":0,"thumbsUpTotal":1,"wouldTakeAgain":1}}],"pageInfo":{"endCursor":"YXJyYXljb25uZWN0aW9uOjk=","hasNextPage":True}}}}}

def test_parse_professors():
    profs, page_info, result_count = parse_professors(MOCK_PROFESSOR_DATA)
    assert len(profs) == 1
    assert result_count == 6340
    assert page_info["hasNextPage"] is True
    assert page_info["endCursor"] == "YXJyYXljb25uZWN0aW9uOjI0"
    
    prof = profs[0]
    assert prof.id == "VGVhY2hlci0zMTE4NDM2"
    assert prof.first_name == "Aaron"
    assert prof.last_name == "Hoskins"
    assert prof.avg_difficulty == 4.2
    assert prof.num_ratings == 62
    
def test_parse_ratings():
    ratings, page_info = parse_ratings(MOCK_RATINGS_DATA)
    assert len(ratings) == 1
    assert page_info["hasNextPage"] is True
    
    rating = ratings[0]
    assert rating.id == "UmF0aW5nLTQyMjA2MzAx"
    assert "Accessible outside class" in rating.rating_tags
    assert "Lots of homework" in rating.rating_tags
    assert rating.course_class == "COP3223C"

def test_parse_ratings_no_tags():
    data = {"data": {"node": {"ratings": {"edges": [{"node": {"id": "1", "clarityRating": 5, "class": "Test", "comment": "", "date": "test", "difficultyRating": 5, "helpfulRating": 5, "isForCredit": True, "isForOnlineClass": False}}]}}}}
    ratings, page_info = parse_ratings(data)
    assert len(ratings) == 1
    assert ratings[0].rating_tags == []
