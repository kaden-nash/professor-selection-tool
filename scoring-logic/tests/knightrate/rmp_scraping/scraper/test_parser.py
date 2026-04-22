import pytest
from src.knightrate.rmp_scraping.scraper.parser import (
    parse_professors,
    parse_ratings,
    _normalize_rating_tags,
)

_MOCK_PROFESSOR_DATA = {
    "data": {
        "search": {
            "teachers": {
                "didFallback": False,
                "edges": [
                    {
                        "cursor": "YXJyYXljb25uZWN0aW9uOjIw",
                        "node": {
                            "__typename": "Teacher",
                            "avgDifficulty": 4.2,
                            "avgRating": 1.1,
                            "department": "Engineering",
                            "firstName": "Aaron",
                            "id": "VGVhY2hlci0zMTE4NDM2",
                            "isSaved": False,
                            "lastName": "Hoskins",
                            "legacyId": 3118436,
                            "numRatings": 62,
                            "school": {"id": "U2Nob29sLTEwODI=", "name": "University of Central Florida"},
                            "wouldTakeAgainPercent": 3.2258,
                        },
                    }
                ],
                "pageInfo": {"endCursor": "YXJyYXljb25uZWN0aW9uOjI0", "hasNextPage": True},
                "resultCount": 6340,
            }
        }
    }
}

_MOCK_RATINGS_DATA = {
    "data": {
        "node": {
            "ratings": {
                "edges": [
                    {
                        "cursor": "YXJyYXljb25uZWN0aW9uOjU=",
                        "node": {
                            "__typename": "Rating",
                            "attendanceMandatory": "non mandatory",
                            "clarityRating": 5,
                            "class": "COP3223C",
                            "comment": "Ahmed was a great choice.",
                            "date": "2025-12-12 15:34:23 +0000 UTC",
                            "difficultyRating": 4,
                            "grade": "A",
                            "helpfulRating": 5,
                            "id": "UmF0aW5nLTQyMjA2MzAx",
                            "isForCredit": True,
                            "isForOnlineClass": False,
                            "ratingTags": "Accessible outside class--Lots of homework",
                            "teacherNote": None,
                            "textbookUse": -1,
                            "thumbs": [],
                            "thumbsDownTotal": 0,
                            "thumbsUpTotal": 1,
                            "wouldTakeAgain": 1,
                        },
                    }
                ],
                "pageInfo": {"endCursor": "YXJyYXljb25uZWN0aW9uOjk=", "hasNextPage": True},
            }
        }
    }
}


class TestParseProfessors:
    """Tests for parse_professors."""

    def test_parses_valid_data(self):
        profs, page_info, result_count = parse_professors(_MOCK_PROFESSOR_DATA)
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

    def test_skips_malformed_nodes(self):
        data = {
            "data": {
                "search": {
                    "teachers": {
                        "edges": [{"node": {"bad": "data"}}],
                        "pageInfo": {"hasNextPage": False},
                        "resultCount": 1,
                    }
                }
            }
        }
        profs, page_info, _ = parse_professors(data)
        assert profs == []
        assert page_info["hasNextPage"] is False

    def test_empty_edges(self):
        data = {
            "data": {
                "search": {
                    "teachers": {
                        "edges": [],
                        "pageInfo": {"hasNextPage": False, "endCursor": ""},
                        "resultCount": 0,
                    }
                }
            }
        }
        profs, _, count = parse_professors(data)
        assert profs == []
        assert count == 0

    def test_missing_data_key_returns_defaults(self):
        profs, page_info, count = parse_professors({})
        assert profs == []
        assert count == 0
        assert page_info["hasNextPage"] is False


class TestParseRatings:
    """Tests for parse_ratings."""

    def test_parses_valid_data(self):
        ratings, page_info = parse_ratings(_MOCK_RATINGS_DATA)
        assert len(ratings) == 1
        assert page_info["hasNextPage"] is True

        rating = ratings[0]
        assert rating.id == "UmF0aW5nLTQyMjA2MzAx"
        assert "Accessible outside class" in rating.rating_tags
        assert "Lots of homework" in rating.rating_tags
        assert rating.course_class == "COP3223C"

    def test_empty_rating_tags_string(self):
        data = {
            "data": {
                "node": {
                    "ratings": {
                        "edges": [
                            {
                                "node": {
                                    "id": "1",
                                    "clarityRating": 5,
                                    "class": "Test",
                                    "comment": "",
                                    "date": "test",
                                    "difficultyRating": 5,
                                    "helpfulRating": 5,
                                    "isForCredit": True,
                                    "isForOnlineClass": False,
                                }
                            }
                        ]
                    }
                }
            }
        }
        ratings, _ = parse_ratings(data)
        assert len(ratings) == 1
        assert ratings[0].rating_tags == []

    def test_rating_tags_as_list(self):
        data = {
            "data": {
                "node": {
                    "ratings": {
                        "edges": [
                            {
                                "node": {
                                    "id": "2",
                                    "clarityRating": 5,
                                    "class": "Test",
                                    "comment": "",
                                    "date": "test",
                                    "difficultyRating": 5,
                                    "helpfulRating": 5,
                                    "isForCredit": True,
                                    "isForOnlineClass": False,
                                    "ratingTags": ["Good Feedback", "Caring"],
                                }
                            }
                        ]
                    }
                }
            }
        }
        ratings, _ = parse_ratings(data)
        assert ratings[0].rating_tags == ["Good Feedback", "Caring"]

    def test_skips_malformed_rating_nodes(self):
        data = {
            "data": {
                "node": {
                    "ratings": {
                        "edges": [{"node": {"id": "bad"}}],
                        "pageInfo": {"hasNextPage": False},
                    }
                }
            }
        }
        ratings, _ = parse_ratings(data)
        assert ratings == []


class TestNormalizeRatingTags:
    """Tests for the _normalize_rating_tags helper."""

    def test_splits_delimited_string(self):
        result = _normalize_rating_tags("Tag A--Tag B--Tag C")
        assert result == ["Tag A", "Tag B", "Tag C"]

    def test_empty_string_returns_empty_list(self):
        assert _normalize_rating_tags("") == []

    def test_passthrough_list(self):
        assert _normalize_rating_tags(["A", "B"]) == ["A", "B"]

    def test_none_returns_empty_list(self):
        assert _normalize_rating_tags(None) == []

    def test_integer_input_returns_empty_list(self):
        assert _normalize_rating_tags(42) == []
