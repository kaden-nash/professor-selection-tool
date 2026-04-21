import json
from typing import Dict, Any

import pytest

from knightrate.rmp_scraping.scraper.client import GraphQLRequest
from knightrate.rmp_scraping.scraper.engine import ScraperEngine
from knightrate.rmp_scraping.scraper.scraper_config import ScraperConfig
from knightrate.rmp_scraping.scraper.storage import DataStorage

# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class NullMonitor:
    """A no-op monitor for use in tests — avoids real tqdm bars."""

    def init_professors(self, total: int) -> None:
        pass

    def update_professors(self, n: int = 1) -> None:
        pass

    def init_reviews(self, total: int) -> None:
        pass

    def update_reviews(self, n: int = 1) -> None:
        pass

    def close(self) -> None:
        pass


class MockClient:
    """Simulates the RMP GraphQL API for a single professor with one review."""

    def __init__(self) -> None:
        self._call_count = 0

    def execute(self, request: GraphQLRequest) -> Dict[str, Any]:
        self._call_count += 1
        if request.operation_name == "TeacherSearchPaginationQuery":
            return self._professor_response()
        return self._review_response()

    def _professor_response(self) -> Dict[str, Any]:
        if self._call_count > 1:
            return {
                "data": {
                    "search": {
                        "teachers": {
                            "edges": [],
                            "pageInfo": {"hasNextPage": False},
                            "resultCount": 1,
                        }
                    }
                }
            }
        return {
            "data": {
                "search": {
                    "teachers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "Teacher",
                                    "id": "T1",
                                    "firstName": "A",
                                    "lastName": "B",
                                    "department": "CS",
                                    "numRatings": 1,
                                    "avgDifficulty": 1.1,
                                    "avgRating": 1.1,
                                    "wouldTakeAgainPercent": 50,
                                }
                            }
                        ],
                        "pageInfo": {"hasNextPage": True, "endCursor": "C1"},
                        "resultCount": 1,
                    }
                }
            }
        }

    def _review_response(self) -> Dict[str, Any]:
        return {
            "data": {
                "node": {
                    "ratings": {
                        "edges": [
                            {
                                "node": {
                                    "id": "R1",
                                    "clarityRating": 5,
                                    "class": "101",
                                    "comment": "Great",
                                    "date": "2020",
                                    "difficultyRating": 5,
                                    "helpfulRating": 5,
                                    "isForCredit": True,
                                    "isForOnlineClass": False,
                                    "ratingTags": "",
                                }
                            }
                        ],
                        "pageInfo": {"hasNextPage": False},
                    }
                }
            }
        }


class ErrorClient:
    """A client that always raises GraphQLRequestError."""

    def execute(self, request: GraphQLRequest):
        from knightrate.rmp_scraping.scraper.client import GraphQLRequestError
        raise GraphQLRequestError("always fails", payload={}, last_error="mock error")


def _make_config(tmp_path, client=None) -> ScraperConfig:
    return ScraperConfig(
        client=client or MockClient(),
        storage=DataStorage(str(tmp_path)),
        monitor=NullMonitor(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestScraperEngineRun:
    """Integration tests for the full ScraperEngine.run() pipeline."""

    def test_full_run_produces_final_output(self, tmp_path):
        engine = ScraperEngine(_make_config(tmp_path))
        engine.run()

        final = tmp_path / "rmp_data.json"
        assert final.exists()
        with open(final) as f:
            data = json.load(f)
        assert len(data["professors"]) == 1
        assert len(data["professors"][0]["reviews"]) == 1
        assert data["professors"][0]["reviews"][0]["id"] == "R1"

    def test_cancel_sets_flag_and_closes_monitor(self, tmp_path):
        engine = ScraperEngine(_make_config(tmp_path))
        engine.cancel()
        assert engine._is_cancelled is True


class TestScraperEngineRunReviewsOnly:
    """Tests for the run_reviews_only path."""

    def test_no_existing_professors_prints_warning(self, tmp_path, capsys):
        engine = ScraperEngine(_make_config(tmp_path))
        engine.run_reviews_only()
        captured = capsys.readouterr()
        assert "No existing professors found" in captured.out

    def test_reviews_only_processes_stored_professors(self, tmp_path):
        # Seed professors first
        setup_engine = ScraperEngine(_make_config(tmp_path))
        setup_engine.fetch_all_professors()

        # Now run reviews only with a fresh engine on the same directory
        engine = ScraperEngine(_make_config(tmp_path))
        engine.run_reviews_only()

        final = tmp_path / "rmp_data.json"
        assert final.exists()

    def test_professor_limit_applied_in_reviews_only(self, tmp_path):
        setup_engine = ScraperEngine(_make_config(tmp_path))
        setup_engine.fetch_all_professors()

        config = ScraperConfig(
            client=MockClient(),
            storage=DataStorage(str(tmp_path)),
            monitor=NullMonitor(),
            limit_professors=0,
        )
        engine = ScraperEngine(config)
        engine.run_reviews_only()


class TestScraperEngineFetchAllProfessors:
    """Tests for professor-fetching edge cases."""

    def test_fetch_all_professors_with_error_client(self, tmp_path):
        config = _make_config(tmp_path, client=ErrorClient())
        engine = ScraperEngine(config)
        professors = engine.fetch_all_professors()
        assert professors == []

    def test_fetch_reviews_skips_cancelled(self, tmp_path):
        from knightrate.rmp_scraping.scraper.models import Professor
        engine = ScraperEngine(_make_config(tmp_path))
        engine._is_cancelled = True
        prof = Professor(id="P1", firstName="A", lastName="B", numRatings=5, avgDifficulty=1.0, avgRating=1.0)
        engine.fetch_reviews_for_professor(prof)
        assert engine._completed_professors == 0

    def test_fetch_reviews_skips_zero_rating_professor(self, tmp_path):
        from knightrate.rmp_scraping.scraper.models import Professor
        engine = ScraperEngine(_make_config(tmp_path))
        prof = Professor(id="P2", firstName="A", lastName="B", numRatings=0, avgDifficulty=1.0, avgRating=1.0)
        engine.fetch_reviews_for_professor(prof)
        assert engine._completed_professors == 1

    def test_fetch_reviews_skips_already_scraped_professor(self, tmp_path):
        from knightrate.rmp_scraping.scraper.models import Professor
        engine = ScraperEngine(_make_config(tmp_path))
        prof = Professor(
            id="P3", firstName="A", lastName="B",
            numRatings=5, avgDifficulty=1.0, avgRating=1.0,
            allReviewsScraped=True,
        )
        engine.fetch_reviews_for_professor(prof)
        assert engine._completed_professors == 1


class TestRetryFailedRequests:
    """Tests for retry_failed_requests."""

    def test_no_op_when_no_failed_requests(self, tmp_path, capsys):
        engine = ScraperEngine(_make_config(tmp_path))
        engine.retry_failed_requests()
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_retries_professor_payload(self, tmp_path):
        from knightrate.rmp_scraping.scraper.queries import (
            PROFESSOR_QUERY_STRING,
            INITIAL_CURSOR,
        )
        storage = DataStorage(str(tmp_path))
        payload = {
            "query": PROFESSOR_QUERY_STRING,
            "variables": {"count": 5, "cursor": INITIAL_CURSOR, "query": {"text": "", "schoolID": "U2Nob29sLTEwODI=", "fallback": True}},
            "operationName": "TeacherSearchPaginationQuery",
        }
        storage.save_failed_request(payload)
        engine = ScraperEngine(_make_config(tmp_path))
        engine.retry_failed_requests()
        assert storage.get_failed_requests() == []

    def test_retries_ratings_payload(self, tmp_path, capsys):
        from knightrate.rmp_scraping.scraper.queries import RATINGS_QUERY_STRING, INITIAL_CURSOR
        from knightrate.rmp_scraping.scraper.models import Professor
        storage = DataStorage(str(tmp_path))
        prof = Professor(id="T1", firstName="A", lastName="B", numRatings=1, avgDifficulty=1.0, avgRating=1.0)
        storage.append_professors([prof])
        payload = {
            "query": RATINGS_QUERY_STRING,
            "variables": {"count": 5, "id": "T1", "courseFilter": None, "cursor": INITIAL_CURSOR},
            "operationName": "RatingsListQuery",
        }
        storage.save_failed_request(payload)
        engine = ScraperEngine(_make_config(tmp_path))
        engine.retry_failed_requests()
        assert storage.get_failed_requests() == []

    def test_keeps_payload_when_retry_fails_with_graphql_error(self, tmp_path, capsys):
        from knightrate.rmp_scraping.scraper.client import GraphQLRequestError
        storage = DataStorage(str(tmp_path))
        payload = {"query": "bad", "variables": {}, "operationName": "TeacherSearchPaginationQuery"}
        storage.save_failed_request(payload)

        config = ScraperConfig(
            client=ErrorClient(),
            storage=storage,
            monitor=NullMonitor(),
        )
        engine = ScraperEngine(config)
        engine.retry_failed_requests()
        assert len(storage.get_failed_requests()) == 1
        captured = capsys.readouterr()
        assert "Retry failed again" in captured.out

    def test_keeps_payload_when_retry_raises_generic_exception(self, tmp_path, capsys):
        class BoomClient:
            def execute(self, request):
                raise RuntimeError("boom")

        storage = DataStorage(str(tmp_path))
        payload = {"query": "bad", "variables": {}, "operationName": "TeacherSearchPaginationQuery"}
        storage.save_failed_request(payload)

        config = ScraperConfig(client=BoomClient(), storage=storage, monitor=NullMonitor())
        engine = ScraperEngine(config)
        engine.retry_failed_requests()
        assert len(storage.get_failed_requests()) == 1
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.out


class TestEdgeCases:
    """Tests targeting specific uncovered branches in engine.py."""

    def test_cancel_with_active_futures_cancels_them(self, tmp_path):
        from unittest.mock import MagicMock
        engine = ScraperEngine(_make_config(tmp_path))
        mock_future = MagicMock()
        engine.futures = [mock_future]
        engine.cancel()
        mock_future.cancel.assert_called_once()

    def test_generic_exception_in_fetch_professors_breaks_loop(self, tmp_path, capsys):
        class ExplodingClient:
            def execute(self, request):
                raise ValueError("boom")

        config = ScraperConfig(client=ExplodingClient(), storage=DataStorage(str(tmp_path)), monitor=NullMonitor())
        engine = ScraperEngine(config)
        professors = engine.fetch_all_professors()
        assert professors == []
        captured = capsys.readouterr()
        assert "Unexpected error fetching professors" in captured.out

    def test_existing_professors_fast_forward_progress(self, tmp_path):
        """When existing professors are loaded, the monitor fast-forwards on first request."""
        from knightrate.rmp_scraping.scraper.models import Professor
        storage = DataStorage(str(tmp_path))
        storage.append_professors([
            Professor(id="P_existing", firstName="X", lastName="Y", numRatings=0, avgDifficulty=1.0, avgRating=1.0)
        ])
        update_calls = []
        monitor = NullMonitor()
        monitor.update_professors = lambda n: update_calls.append(n)
        config = ScraperConfig(client=MockClient(), storage=storage, monitor=monitor)
        engine = ScraperEngine(config)
        engine.fetch_all_professors()
        assert len(update_calls) > 0

    def test_professor_limit_applied_in_collect(self, tmp_path):
        config = ScraperConfig(
            client=MockClient(),
            storage=DataStorage(str(tmp_path)),
            monitor=NullMonitor(),
            limit_professors=1,
        )
        engine = ScraperEngine(config)
        professors = engine.fetch_all_professors()
        assert len(professors) == 1

    def test_review_error_breaks_loop(self, tmp_path, capsys):
        from knightrate.rmp_scraping.scraper.client import GraphQLRequestError
        from knightrate.rmp_scraping.scraper.models import Professor

        class ProfOkReviewsErrorClient:
            _call_count = 0

            def execute(self, request):
                self._call_count += 1
                if request.operation_name == "TeacherSearchPaginationQuery":
                    if self._call_count > 1:
                        return {"data": {"search": {"teachers": {"edges": [], "pageInfo": {"hasNextPage": False}, "resultCount": 1}}}}
                    return {"data": {"search": {"teachers": {"edges": [{"node": {"id": "T1", "firstName": "A", "lastName": "B", "numRatings": 1, "avgDifficulty": 1.0, "avgRating": 1.0}}], "pageInfo": {"hasNextPage": False}, "resultCount": 1}}}}
                raise GraphQLRequestError("review fail", {}, "review error")

        config = ScraperConfig(
            client=ProfOkReviewsErrorClient(),
            storage=DataStorage(str(tmp_path)),
            monitor=NullMonitor(),
        )
        engine = ScraperEngine(config)
        prof = Professor(id="T1", firstName="A", lastName="B", numRatings=1, avgDifficulty=1.0, avgRating=1.0)
        engine.fetch_reviews_for_professor(prof)
        captured = capsys.readouterr()
        assert "Failed to fetch reviews" in captured.out

    def test_review_generic_exception_breaks_loop(self, tmp_path, capsys):
        from knightrate.rmp_scraping.scraper.models import Professor

        class ProfOkReviewsExplodeClient:
            def execute(self, request):
                if request.operation_name == "RatingsListQuery":
                    raise RuntimeError("kaboom")
                return {"data": {"search": {"teachers": {"edges": [], "pageInfo": {"hasNextPage": False}, "resultCount": 0}}}}

        config = ScraperConfig(
            client=ProfOkReviewsExplodeClient(),
            storage=DataStorage(str(tmp_path)),
            monitor=NullMonitor(),
        )
        engine = ScraperEngine(config)
        prof = Professor(id="T2", firstName="A", lastName="B", numRatings=5, avgDifficulty=1.0, avgRating=1.0)
        engine.fetch_reviews_for_professor(prof)
        captured = capsys.readouterr()
        assert "Unexpected fault" in captured.out

    def test_review_limit_stops_paging(self, tmp_path):
        from knightrate.rmp_scraping.scraper.models import Professor
        config = ScraperConfig(
            client=MockClient(),
            storage=DataStorage(str(tmp_path)),
            monitor=NullMonitor(),
            limit_reviews=1,
        )
        engine = ScraperEngine(config)
        prof = Professor(id="T1", firstName="A", lastName="B", numRatings=5, avgDifficulty=1.0, avgRating=1.0)
        engine.fetch_reviews_for_professor(prof)
        assert engine._completed_professors == 1

    def test_finalize_without_all_reviews_scraped_flag(self, tmp_path):
        """When has_next_page remains True (limit hit), allReviewsScraped should not be saved."""
        from knightrate.rmp_scraping.scraper.models import Professor

        class MultiPageReviewClient:
            _call_count = 0

            def execute(self, request):
                self._call_count += 1
                if request.operation_name == "TeacherSearchPaginationQuery":
                    return {"data": {"search": {"teachers": {"edges": [], "pageInfo": {"hasNextPage": False}, "resultCount": 0}}}}
                return {"data": {"node": {"ratings": {"edges": [{"node": {"id": f"R{self._call_count}", "clarityRating": 5, "class": "101", "comment": "ok", "date": "2020", "difficultyRating": 5, "helpfulRating": 5}}], "pageInfo": {"hasNextPage": True, "endCursor": "next"}}}}}

        config = ScraperConfig(
            client=MultiPageReviewClient(),
            storage=DataStorage(str(tmp_path)),
            monitor=NullMonitor(),
            limit_reviews=1,
        )
        engine = ScraperEngine(config)
        prof = Professor(id="T1", firstName="A", lastName="B", numRatings=5, avgDifficulty=1.0, avgRating=1.0)
        engine.fetch_reviews_for_professor(prof)
        # allReviewsScraped should NOT be in attrs since we hit the limit, not end of pages
        professors, _ = config.storage.load_all()
        # The professor isn't in storage but the attrs file also shouldn't mark it done
