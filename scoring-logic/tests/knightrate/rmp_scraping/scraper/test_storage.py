import json
import os

import pytest

from src.knightrate.rmp_scraping.scraper.models import Professor, Rating
from src.knightrate.rmp_scraping.scraper.storage import DataStorage


def _make_professor(prof_id: str = "P1", num_ratings: int = 1) -> Professor:
    return Professor(
        id=prof_id,
        firstName="Alice",
        lastName="Smith",
        numRatings=num_ratings,
        avgDifficulty=2.0,
        avgRating=4.0,
    )


def _make_rating(rating_id: str = "R1", prof_id: str = "P1") -> Rating:
    return Rating(
        id=rating_id,
        prof_id=prof_id,
        clarityRating=5.0,
        comment="Great",
        date="2024-01-01",
        difficultyRating=2.0,
        helpfulRating=5.0,
    )


class TestDataStorageWriteAndLoad:
    """Tests for DataStorage write/load round-trips."""

    def test_append_and_load_professors(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        prof = _make_professor()
        storage.append_professors([prof])
        professors, metadata = storage.load_all()
        assert len(professors) == 1
        assert professors[0].id == "P1"
        assert metadata == {}

    def test_duplicate_professors_deduped_on_load(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        prof = _make_professor()
        storage.append_professors([prof, prof])
        professors, _ = storage.load_all()
        assert len(professors) == 1

    def test_append_reviews(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        rating = _make_rating()
        storage.append_reviews([rating])
        assert os.path.exists(storage.review_file)
        with open(storage.review_file, encoding="utf-8") as f:
            data = json.loads(f.readline())
        assert data["id"] == "R1"

    def test_append_prof_attrs_marks_reviews_scraped(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.append_professors([_make_professor()])
        storage.append_prof_attrs("P1", {"allReviewsScraped": True})
        professors, _ = storage.load_all()
        assert professors[0].all_reviews_scraped is True

    def test_attrs_deduplication_only_first_applies(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.append_professors([_make_professor()])
        storage.append_prof_attrs("P1", {"allReviewsScraped": True})
        storage.append_prof_attrs("P1", {"allReviewsScraped": False})
        professors, _ = storage.load_all()
        assert professors[0].all_reviews_scraped is True

    def test_load_all_with_no_files(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        professors, metadata = storage.load_all()
        assert professors == []
        assert metadata == {}

    def test_load_all_ignores_blank_lines(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        with open(storage.prof_file, "w", encoding="utf-8") as f:
            f.write("\n\n")
        professors, _ = storage.load_all()
        assert professors == []

    def test_save_professors_overwrites_file(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.append_professors([_make_professor("P1")])
        new_prof = _make_professor("P2")
        storage.save_professors([new_prof])
        professors, _ = storage.load_all()
        assert len(professors) == 1
        assert professors[0].id == "P2"


class TestDataStorageFailedRequests:
    """Tests for failed-request queue operations."""

    def test_save_and_get_failed_request(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        payload = {"query": "q", "variables": {}, "operationName": "Test"}
        storage.save_failed_request(payload)
        result = storage.get_failed_requests()
        assert len(result) == 1
        assert result[0]["operationName"] == "Test"

    def test_get_failed_requests_returns_empty_when_no_file(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        assert storage.get_failed_requests() == []

    def test_overwrite_failed_requests_replaces_content(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.save_failed_request({"a": 1})
        storage.overwrite_failed_requests([{"b": 2}])
        result = storage.get_failed_requests()
        assert result == [{"b": 2}]

    def test_overwrite_with_empty_list_removes_file(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.save_failed_request({"a": 1})
        storage.overwrite_failed_requests([])
        assert not os.path.exists(storage._failed_file)

    def test_overwrite_no_op_when_file_absent(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.overwrite_failed_requests([])
        assert not os.path.exists(storage._failed_file)

    def test_corrupted_failed_file_returns_empty(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        with open(storage._failed_file, "w") as f:
            f.write("not-json")
        assert storage.get_failed_requests() == []


class TestDataStorageCorrelate:
    """Tests for correlate_data."""

    def test_correlate_produces_final_output(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        prof = _make_professor()
        storage.append_professors([prof])
        rating = _make_rating()
        storage.append_reviews([rating])
        storage.correlate_data()

        assert os.path.exists(storage.final_file)
        with open(storage.final_file, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["professors"]) == 1
        assert len(data["professors"][0]["reviews"]) == 1

    def test_correlate_deduplicates_reviews(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.append_professors([_make_professor()])
        storage.append_reviews([_make_rating(), _make_rating()])
        storage.correlate_data()

        with open(storage.final_file, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["professors"][0]["reviews"]) == 1

    def test_correlate_with_no_reviews_file(self, tmp_path):
        storage = DataStorage(str(tmp_path))
        storage.append_professors([_make_professor()])
        storage.correlate_data()

        with open(storage.final_file, encoding="utf-8") as f:
            data = json.load(f)
        assert data["professors"][0]["reviews"] == []
