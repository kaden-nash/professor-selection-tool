import concurrent.futures
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

from .client import GraphQLRequest, GraphQLRequestError
from .models import Professor, Rating
from .parser import parse_professors, parse_ratings
from .queries import (
    INITIAL_CURSOR,
    PROFESSOR_QUERY_STRING,
    PROFESSOR_OPERATION,
    RATINGS_QUERY_STRING,
    RATINGS_OPERATION,
    build_professor_variables,
    build_review_variables,
)
from .scraper_config import ScraperConfig

_BUFFER_FLUSH_SIZE = 50
_MAX_REVIEW_WORKERS = 200
_NO_RATINGS = 0


@dataclass
class _ProfessorFetchState:
    """Mutable state carried through the professor pagination loop."""

    prof_map: Dict[str, Professor]
    seen_ids: set
    buffer: List[Professor] = field(default_factory=list)
    total_count: int = 0
    cursor: str = INITIAL_CURSOR
    has_next_page: bool = True
    is_first_request: bool = True


@dataclass
class _ReviewFetchState:
    """Mutable state carried through the review pagination loop for one professor."""

    buffer: List[Rating] = field(default_factory=list)
    seen_ids: set = field(default_factory=set)
    total_scraped: int = 0
    cursor: str = INITIAL_CURSOR
    has_next_page: bool = True


class ScraperEngine:
    """Orchestrates the RateMyProfessors professor and review scraping pipeline.

    All scraping configuration (client, storage, monitor, limits) is supplied
    via a single ScraperConfig object so this class stays focused on
    coordination logic rather than wiring.
    """

    def __init__(self, config: ScraperConfig) -> None:
        """Initialises the engine with the given configuration.

        Args:
            config: A ScraperConfig supplying all dependencies and limits.
        """
        self._config = config
        self._result_count: int = 0
        self._completed_professors: int = 0
        self._is_cancelled: bool = False
        self._executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self.futures: List[Any] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def cancel(self) -> None:
        """Signals cancellation, cancels pending futures, and closes the monitor."""
        self._is_cancelled = True
        for future in self.futures:
            future.cancel()
        self._config.monitor.close()

    def run(self) -> None:
        """Runs the full scraping pipeline: professors then reviews."""
        print("Scraping started. Fetching all professors in UCF...")
        professors = self.fetch_all_professors()
        print(f"Fetched {len(professors)} professors. Now fetching reviews...")
        self._config.monitor.init_reviews(len(professors))
        self._run_review_executor(professors)
        print("Exporting data to JSON storage...")
        self._config.storage.correlate_data()

    def run_reviews_only(self) -> None:
        """Fetches reviews using professors already stored in the local database."""
        print("Running in --reviews-only mode. Checking local JSON database...")
        professors, _ = self._config.storage.load_all()
        if not professors:
            print("[!] No existing professors found. Please run with professor scraping enabled first.")
            return
        professors = self._apply_professor_limit(professors)
        print(f"Loaded {len(professors)} professors from JSON. Fetching reviews...")
        self._config.monitor.init_reviews(len(professors))
        self._run_review_executor(professors)
        print("Exporting finalized data to JSON storage...")
        self._config.storage.correlate_data()

    def retry_failed_requests(self) -> None:
        """Retries all previously failed requests and updates stored data."""
        failed_payloads = self._config.storage.get_failed_requests()
        if not failed_payloads:
            return
        print(f"Loading existing data to merge {len(failed_payloads)} retried requests...")
        professors, metadata = self._config.storage.load_all()
        if not professors:
            print("Warning: No existing data found. Retries won't find professor nodes.")
        prof_map = {p.id: p for p in professors}
        still_failed = self._process_failed_payloads(failed_payloads, prof_map)
        self._save_retry_results(professors, metadata, still_failed)

    def fetch_all_professors(self) -> List[Professor]:
        """Fetches all professors from RMP, resuming from any stored checkpoint.

        Returns:
            The full list of professors, loaded fresh from storage after the run.
        """
        state = self._init_professor_fetch_state()
        while True:
            try:
                profs, page_info, count = self._fetch_professor_page(state.cursor)
            except GraphQLRequestError as exc:
                self._handle_professor_request_error(exc)
                break
            except Exception as exc:
                print(f"Unexpected error fetching professors: {exc}")
                break
            self._update_professor_progress_on_first(state, count)
            self._collect_new_professors(profs, state)
            state.cursor = page_info.get("endCursor", "")
            state.has_next_page = page_info.get("hasNextPage", False)
            if self._should_stop_professor_paging(state):
                break
            self._flush_professors_if_needed(state.buffer)
        self._flush_professors_if_needed(state.buffer, force=True)
        print("Professor phase complete. Loading stored indexes...")
        return self._config.storage.load_all()[0]

    def fetch_reviews_for_professor(self, prof: Professor) -> None:
        """Fetches and stores all reviews for the given professor.

        Args:
            prof: The professor whose reviews should be fetched.
        """
        if self._is_cancelled:
            return
        if prof.num_ratings == _NO_RATINGS:
            self._handle_no_ratings_professor(prof)
            return
        if prof.all_reviews_scraped:
            self._increment_completed(prof)
            return
        state = _ReviewFetchState()
        self._fetch_review_loop(prof, state)
        self._flush_reviews_if_needed(state.buffer, force=True)
        self._finalize_professor_reviews(prof, state)

    # ------------------------------------------------------------------
    # Professor fetching — private helpers
    # ------------------------------------------------------------------

    def _init_professor_fetch_state(self) -> _ProfessorFetchState:
        """Loads existing professors from storage to build the initial fetch state.

        Returns:
            A _ProfessorFetchState seeded with any previously scraped professors.
        """
        professors, _ = self._config.storage.load_all()
        prof_map = {p.id: p for p in professors}
        seen_ids = set(prof_map.keys())
        return _ProfessorFetchState(
            prof_map=prof_map,
            seen_ids=seen_ids,
            total_count=len(seen_ids),
        )

    def _fetch_professor_page(self, cursor: str) -> Tuple[List[Professor], Dict, int]:
        """Executes one paginated professor search query.

        Args:
            cursor: The pagination cursor for the page to fetch.

        Returns:
            A tuple of (professors, pageInfo dict, resultCount).
        """
        variables = build_professor_variables(cursor)
        request = GraphQLRequest(PROFESSOR_QUERY_STRING, variables, PROFESSOR_OPERATION)
        data = self._config.client.execute(request)
        return parse_professors(data)

    def _update_professor_progress_on_first(
        self, state: _ProfessorFetchState, count: int
    ) -> None:
        """Initialises the professor progress bar on the first API response.

        Args:
            state: The current fetch state (mutated: is_first_request set False).
            count: The total result count returned by the API.
        """
        if not state.is_first_request:
            return
        limit = self._config.limit_professors
        self._result_count = min(count, limit) if limit is not None else count
        self._config.monitor.init_professors(self._result_count)
        existing = min(state.total_count, self._result_count)
        if existing > 0:
            self._config.monitor.update_professors(existing)
        state.is_first_request = False

    def _collect_new_professors(self, profs: List[Professor], state: _ProfessorFetchState) -> None:
        """Filters professors to new-only and adds them to the state buffer.

        Args:
            profs: Professors returned from the current page.
            state: The fetch state holding the seen-ID set and buffer.
        """
        limit = self._config.limit_professors
        if limit is not None:
            profs = profs[: limit - state.total_count]
        for prof in profs:
            if prof.id not in state.seen_ids:
                state.seen_ids.add(prof.id)
                state.buffer.append(prof)
                state.total_count += 1

    def _should_stop_professor_paging(self, state: _ProfessorFetchState) -> bool:
        """Returns True if professor pagination should stop.

        Args:
            state: The current fetch state.

        Returns:
            True when pagination is exhausted or the professor limit is reached.
        """
        if not state.has_next_page or not state.cursor:
            return True
        limit = self._config.limit_professors
        return limit is not None and state.total_count >= limit

    def _flush_professors_if_needed(
        self, buffer: List[Professor], force: bool = False
    ) -> None:
        """Flushes the professor buffer to storage when full or when forced.

        Args:
            buffer: The in-memory professor buffer (cleared on flush).
            force: When True, flush regardless of the buffer size.
        """
        if not buffer:
            return
        if force or len(buffer) >= _BUFFER_FLUSH_SIZE:
            self._config.storage.append_professors(buffer)
            buffer.clear()

    def _handle_professor_request_error(self, error: GraphQLRequestError) -> None:
        """Logs a professor-page error and saves the failed payload for retry.

        Args:
            error: The GraphQLRequestError that was raised.
        """
        print(f"Failed to fetch professors chunk: {error.last_error}")
        self._config.storage.save_failed_request(error.payload)

    # ------------------------------------------------------------------
    # Review fetching — private helpers
    # ------------------------------------------------------------------

    def _fetch_review_loop(self, prof: Professor, state: _ReviewFetchState) -> None:
        """Runs the review pagination loop for a single professor.

        Args:
            prof: The professor whose reviews are being fetched.
            state: The mutable review fetch state (mutated in-place).
        """
        while True:
            try:
                ratings, page_info = self._fetch_review_page(prof.id, state.cursor)
            except GraphQLRequestError as exc:
                self._handle_review_request_error(prof, exc)
                break
            except Exception as exc:
                print(f"Unexpected fault while fetching reviews for {prof.id}: {exc}")
                break
            self._stamp_ratings_prof_id(ratings, prof.id)
            self._collect_new_reviews(ratings, state)
            state.cursor = page_info.get("endCursor", "")
            state.has_next_page = page_info.get("hasNextPage", False)
            if self._should_stop_review_paging(state):
                break
            self._flush_reviews_if_needed(state.buffer)

    def _stamp_ratings_prof_id(self, ratings: List[Rating], prof_id: str) -> None:
        """Sets the prof_id field on each rating from the enclosing professor.

        Args:
            ratings: The list of Rating objects to stamp.
            prof_id: The professor's RMP node ID to assign.
        """
        for rating in ratings:
            rating.prof_id = prof_id

    def _fetch_review_page(self, prof_id: str, cursor: str) -> Tuple[List[Rating], Dict]:
        """Executes one paginated ratings query for a professor.

        Args:
            prof_id: The RMP professor node ID.
            cursor: The pagination cursor for the page to fetch.

        Returns:
            A tuple of (ratings, pageInfo dict).
        """
        variables = build_review_variables(prof_id, cursor)
        request = GraphQLRequest(RATINGS_QUERY_STRING, variables, RATINGS_OPERATION)
        data = self._config.client.execute(request)
        return parse_ratings(data)

    def _collect_new_reviews(self, ratings: List[Rating], state: _ReviewFetchState) -> None:
        """Filters ratings to new-only and adds them to the state buffer.

        Args:
            ratings: Ratings returned from the current page.
            state: The review fetch state (mutated in-place).
        """
        limit = self._config.limit_reviews
        if limit is not None:
            ratings = ratings[: limit - state.total_scraped]
        for rating in ratings:
            if rating.id not in state.seen_ids:
                state.seen_ids.add(rating.id)
                state.buffer.append(rating)
                state.total_scraped += 1

    def _should_stop_review_paging(self, state: _ReviewFetchState) -> bool:
        """Returns True if review pagination should stop.

        Args:
            state: The current review fetch state.

        Returns:
            True when pagination is exhausted or the review limit is reached.
        """
        if not state.has_next_page or not state.cursor:
            return True
        limit = self._config.limit_reviews
        return limit is not None and state.total_scraped >= limit

    def _flush_reviews_if_needed(
        self, buffer: List[Rating], force: bool = False
    ) -> None:
        """Flushes the review buffer to storage when full or forced.

        Args:
            buffer: The in-memory review buffer (cleared on flush).
            force: When True, flush regardless of the buffer size.
        """
        if not buffer:
            return
        if force or len(buffer) >= _BUFFER_FLUSH_SIZE:
            self._config.storage.append_reviews(buffer)
            buffer.clear()

    def _finalize_professor_reviews(self, prof: Professor, state: _ReviewFetchState) -> None:
        """Marks review scraping complete if fully finished and updates progress.

        Args:
            prof: The professor whose review scraping just ended.
            state: The final review fetch state, used to determine completeness.
        """
        if not state.has_next_page or not state.cursor:
            self._config.storage.append_prof_attrs(prof.id, {"allReviewsScraped": True})
        self._increment_completed(prof)

    def _handle_review_request_error(self, prof: Professor, error: GraphQLRequestError) -> None:
        """Logs a review-page error and saves the failed payload for retry.

        Args:
            prof: The professor whose review request failed.
            error: The GraphQLRequestError that was raised.
        """
        print(f"Failed to fetch reviews for professor {prof.id}: {error.last_error}")
        self._config.storage.save_failed_request(error.payload)

    def _handle_no_ratings_professor(self, prof: Professor) -> None:
        """Marks a zero-rating professor as fully scraped and updates progress.

        Args:
            prof: The professor with no ratings to fetch.
        """
        self._config.storage.append_prof_attrs(prof.id, {"allReviewsScraped": True})
        self._increment_completed(prof)

    def _increment_completed(self, prof: Professor) -> None:
        """Updates the review progress bar and increments the completed-professor count.

        Args:
            prof: The professor that has just been fully processed.
        """
        self._config.monitor.update_reviews(1)
        with self._config.storage.lock:
            self._completed_professors += 1

    # ------------------------------------------------------------------
    # Executor — shared by run() and run_reviews_only()
    # ------------------------------------------------------------------

    def _run_review_executor(self, professors: List[Professor]) -> None:
        """Submits review-fetch tasks for each professor and waits for completion.

        Args:
            professors: The list of professors to fetch reviews for.
        """
        self._is_cancelled = False
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=_MAX_REVIEW_WORKERS)
        self.futures = [
            self._executor.submit(self.fetch_reviews_for_professor, p) for p in professors
        ]
        for future in concurrent.futures.as_completed(self.futures):
            future.result()
        self._executor.shutdown(wait=True)
        self._config.monitor.close()

    def _apply_professor_limit(self, professors: List[Professor]) -> List[Professor]:
        """Slices the professor list to the configured limit if one is set.

        Args:
            professors: The full professor list.

        Returns:
            A possibly-sliced list respecting limit_professors.
        """
        limit = self._config.limit_professors
        if limit is None:
            return professors
        print(f"Applying limit: Only fetching reviews for the first {limit} professors.")
        return professors[:limit]

    # ------------------------------------------------------------------
    # Retry — private helpers
    # ------------------------------------------------------------------

    def _process_failed_payloads(
        self, payloads: List[Dict], prof_map: Dict[str, Professor]
    ) -> List[Dict]:
        """Retries each failed payload and returns those that still fail.

        Args:
            payloads: The list of previously failed request payloads.
            prof_map: In-memory professor dict to update on success.

        Returns:
            A list of payloads that failed again.
        """
        self._config.monitor.init_professors(len(payloads))
        still_failed = []
        for payload in payloads:
            if not self._retry_single_payload(payload, prof_map):
                still_failed.append(payload)
            self._config.monitor.update_professors(1)
        self._config.monitor.close()
        return still_failed

    def _retry_single_payload(self, payload: Dict, prof_map: Dict[str, Professor]) -> bool:
        """Retries one failed request and merges the result into prof_map.

        Args:
            payload: The request payload to retry.
            prof_map: In-memory professor dict to update on success.

        Returns:
            True if the retry succeeded; False otherwise.
        """
        op_name = payload.get("operationName", "Unknown")
        try:
            request = GraphQLRequest(payload["query"], payload["variables"], op_name)
            data = self._config.client.execute(request)
            if op_name == PROFESSOR_OPERATION:
                profs, _, _ = parse_professors(data)
                for prof in profs:
                    if prof.id not in prof_map:
                        prof_map[prof.id] = prof
            elif op_name == RATINGS_OPERATION:
                ratings, _ = parse_ratings(data)
                prof_id = payload["variables"].get("id", "")
                if prof_id in prof_map:
                    prof_map[prof_id].reviews.extend(ratings)
            return True
        except GraphQLRequestError as exc:
            print(f"Retry failed again for {op_name}: {exc.last_error}")
            return False
        except Exception as exc:
            print(f"Unexpected error during retry of {op_name}: {exc}")
            return False

    def _save_retry_results(
        self, professors: List[Professor], metadata: Dict, still_failed: List[Dict]
    ) -> None:
        """Persists merged professors and updates the failed-requests queue.

        Args:
            professors: The updated professor list to persist.
            metadata: Metadata dict (currently unused but kept for forward compat).
            still_failed: Payloads that failed again and must be re-queued.
        """
        print("Saving merged results to JSON storage...")
        self._config.storage.save_professors(professors)
        if still_failed:
            print(f"{len(still_failed)} requests failed again. Saving back to queue.")
            self._config.storage.overwrite_failed_requests(still_failed)
        else:
            print("All failed requests successfully retried and merged!")
            self._config.storage.overwrite_failed_requests([])
