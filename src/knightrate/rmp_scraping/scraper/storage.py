import json
import os
import threading
from typing import List, Dict, Any, Tuple

from .models import Professor, Rating

_PROF_FILENAME = "rmp_prof_data.json"
_REVIEW_FILENAME = "rmp_review_data.json"
_ATTRS_FILENAME = "rmp_prof_attrs.json"
_FINAL_FILENAME = "rmp_data.json"
_FAILED_FILENAME = "failed_requests.json"


class DataStorage:
    """Thread-safe JSON data-storage layer for scraping results.

    Professors, reviews, and attributes are written incrementally to
    newline-delimited JSON (JSONL) files.  A final ``correlate_data``
    call merges everything into a single ``rmp_data.json`` output.
    """

    def __init__(self, output_dir: str | None = None) -> None:
        """Initialises storage pointing at the given output directory.

        Args:
            output_dir: Directory for all output files. Defaults to the
                        package root when None.
        """
        self.base_dir = output_dir or os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.prof_file = os.path.join(self.base_dir, _PROF_FILENAME)
        self.review_file = os.path.join(self.base_dir, _REVIEW_FILENAME)
        self.attrs_file = os.path.join(self.base_dir, _ATTRS_FILENAME)
        self.final_file = os.path.join(self.base_dir, _FINAL_FILENAME)
        self._failed_file = os.path.join(self.base_dir, _FAILED_FILENAME)
        self.lock = threading.RLock()

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def append_professors(self, professors: List[Professor]) -> None:
        """Appends professors to the JSONL professor file (reviews excluded).

        Args:
            professors: The professor objects to persist.
        """
        records = [p.model_dump(by_alias=True, exclude={"reviews"}) for p in professors]
        self._append_jsonl(self.prof_file, records)

    def append_reviews(self, reviews: List[Rating]) -> None:
        """Appends ratings to the JSONL review file.

        Args:
            reviews: The Rating objects to persist.
        """
        records = [r.model_dump(by_alias=True) for r in reviews]
        self._append_jsonl(self.review_file, records)

    def append_prof_attrs(self, prof_id: str, attrs: Dict[str, Any]) -> None:
        """Appends an attribute record for a professor to the attrs JSONL file.

        Args:
            prof_id: The professor's RMP node ID.
            attrs: Attribute key/value pairs to record (e.g. allReviewsScraped).
        """
        record = {"prof_id": prof_id, **attrs}
        self._append_jsonl(self.attrs_file, [record])

    def save_professors(self, professors: List[Professor]) -> None:
        """Overwrites the professor file with the given list (reviews excluded).

        Args:
            professors: The complete professor list to persist.
        """
        with self.lock:
            with open(self.prof_file, "w", encoding="utf-8") as f:
                for prof in professors:
                    record = prof.model_dump(by_alias=True, exclude={"reviews"})
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def save_failed_request(self, payload: Dict[str, Any]) -> None:
        """Appends a failed request payload to the failed-requests JSON file.

        Args:
            payload: The request payload that failed.
        """
        with self.lock:
            data = self._read_failed_requests_unsafe()
            data.append(payload)
            self._write_failed_requests_unsafe(data)

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def load_all(self) -> Tuple[List[Professor], Dict[str, Any]]:
        """Loads all professors from the JSONL files and applies stored attributes.

        Returns:
            A tuple of (professor list, empty metadata dict).
        """
        prof_map = self._load_professors()
        self._apply_attrs(prof_map)
        return list(prof_map.values()), {}

    def get_failed_requests(self) -> List[Dict[str, Any]]:
        """Returns the list of previously failed request payloads.

        Returns:
            A list of payload dicts, or an empty list if none exist.
        """
        with self.lock:
            return self._read_failed_requests_unsafe()

    def overwrite_failed_requests(self, payloads: List[Dict[str, Any]]) -> None:
        """Replaces the failed-requests file with a new payload list.

        Passing an empty list removes the file entirely.

        Args:
            payloads: Replacement list of failed payloads.
        """
        with self.lock:
            if not payloads:
                if os.path.exists(self._failed_file):
                    os.remove(self._failed_file)
            else:
                self._write_failed_requests_unsafe(payloads)

    # ------------------------------------------------------------------
    # Correlation
    # ------------------------------------------------------------------

    def correlate_data(self) -> None:
        """Merges all split data files into the final rmp_data.json.

        Loads professors and reviews, deduplicates reviews, rewrites the
        review file without duplicates, and serialises the merged result.
        """
        print("Correlating split data files into the final rmp_data.json...")
        professors, _ = self.load_all()
        prof_map: Dict[str, Professor] = {p.id: p for p in professors}

        dedup_reviews = self._load_and_attach_reviews(prof_map)
        if dedup_reviews:
            self._rewrite_review_file(dedup_reviews)

        self._write_final_output(prof_map)
        print(f"Done. Final output generated at {self.final_file}.")

    # ------------------------------------------------------------------
    # Private — load helpers
    # ------------------------------------------------------------------

    def _load_professors(self) -> Dict[str, Professor]:
        """Reads the professor JSONL file into a dict keyed by professor ID.

        Returns:
            A dict mapping professor ID to Professor objects.
        """
        prof_map: Dict[str, Professor] = {}
        if not os.path.exists(self.prof_file):
            return prof_map
        with open(self.prof_file, "r", encoding="utf-8") as f:
            for line in f:
                self._parse_professor_line(line, prof_map)
        return prof_map

    def _parse_professor_line(self, line: str, prof_map: Dict[str, Professor]) -> None:
        """Parses one JSONL line and inserts the professor into prof_map.

        Args:
            line: A single line from the professor JSONL file.
            prof_map: The dict to insert successfully parsed professors into.
        """
        if not line.strip():
            return
        try:
            prof = Professor(**json.loads(line))
            prof_map[prof.id] = prof
        except Exception:
            pass

    def _apply_attrs(self, prof_map: Dict[str, Professor]) -> None:
        """Reads the attrs file and marks professors whose reviews are fully scraped.

        Args:
            prof_map: The in-memory professor dict to update.
        """
        if not os.path.exists(self.attrs_file):
            return
        seen_ids: set = set()
        with open(self.attrs_file, "r", encoding="utf-8") as f:
            for line in f:
                self._apply_attr_line(line, prof_map, seen_ids)

    def _apply_attr_line(self, line: str, prof_map: Dict[str, Professor], seen_ids: set) -> None:
        """Applies a single attribute record to its professor if not already seen.

        Args:
            line: A single line from the attrs JSONL file.
            prof_map: The in-memory professor dict to update.
            seen_ids: Set of professor IDs that have already had attrs applied.
        """
        if not line.strip():
            return
        try:
            data = json.loads(line)
            pid = data.get("prof_id")
            if pid and pid in prof_map and pid not in seen_ids:
                if data.get("allReviewsScraped"):
                    prof_map[pid].all_reviews_scraped = True
                    seen_ids.add(pid)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Private — correlate helpers
    # ------------------------------------------------------------------

    def _load_and_attach_reviews(self, prof_map: Dict[str, Professor]) -> List[Dict]:
        """Reads the review JSONL file and attaches unique reviews to professors.

        Args:
            prof_map: The in-memory professor dict to attach reviews to.

        Returns:
            A deduplicated list of raw review record dicts.
        """
        seen_ids: set = set()
        dedup: List[Dict] = []
        if not os.path.exists(self.review_file):
            return dedup
        with open(self.review_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    r_data = json.loads(line)
                    r_id = r_data.get("id")
                    pid = r_data.get("prof_id")
                    if pid and pid in prof_map and r_id not in seen_ids:
                        prof_map[pid].reviews.append(Rating(**r_data))
                        seen_ids.add(r_id)
                        dedup.append(r_data)
                except Exception:
                    pass
        return dedup

    def _rewrite_review_file(self, dedup_reviews: List[Dict]) -> None:
        """Overwrites the review JSONL file with deduplicated records.

        Args:
            dedup_reviews: The deduplicated list of raw review dicts to write.
        """
        with self.lock:
            with open(self.review_file, "w", encoding="utf-8") as f:
                for item in dedup_reviews:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def _write_final_output(self, prof_map: Dict[str, Professor]) -> None:
        """Serialises the professor map (with reviews) to the final JSON file.

        Args:
            prof_map: The complete in-memory professor dict to serialise.
        """
        output = {"professors": [p.model_dump(by_alias=True) for p in prof_map.values()]}
        with open(self.final_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Private — JSONL / file I/O primitives
    # ------------------------------------------------------------------

    def _append_jsonl(self, filepath: str, records: List[Dict[str, Any]]) -> None:
        """Appends dicts as JSON lines to a file under the storage lock.

        Args:
            filepath: Absolute path to the target JSONL file.
            records: Dicts to append, one per line.
        """
        if not records:
            return
        with self.lock:
            with open(filepath, "a", encoding="utf-8") as f:
                for item in records:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def _read_failed_requests_unsafe(self) -> List[Dict[str, Any]]:
        """Reads the failed-requests file without acquiring the lock.

        Returns:
            A list of payload dicts, or an empty list if the file is absent/invalid.
        """
        if not os.path.exists(self._failed_file):
            return []
        with open(self._failed_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _write_failed_requests_unsafe(self, payloads: List[Dict[str, Any]]) -> None:
        """Writes payloads to the failed-requests file without acquiring the lock.

        Args:
            payloads: List of payload dicts to persist.
        """
        with open(self._failed_file, "w", encoding="utf-8") as f:
            json.dump(payloads, f, indent=4, ensure_ascii=False)
