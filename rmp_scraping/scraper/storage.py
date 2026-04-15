import json
import os
import threading
from typing import List, Dict, Any, Tuple
from scraper.models import Professor, Rating 

class DataStorage:
    def __init__(self, output_dir: str | None = None):
        """
        Thread-safe JSON data storage for scraping results.

        Args:
            output_dir: Directory where all output files are written.
                        Defaults to the directory containing main.py (legacy behaviour).
        """
        self.base_dir = output_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prof_file = os.path.join(self.base_dir, "rmp_prof_data.json")
        self.review_file = os.path.join(self.base_dir, "rmp_review_data.json")
        self.attrs_file = os.path.join(self.base_dir, "rmp_prof_attrs.json")
        self.final_file = os.path.join(self.base_dir, "rmp_data.json")
        self.lock = threading.RLock()
        
    def _append_jsonl(self, filepath: str, data_list: List[Dict[str, Any]]):
        """Helper to append dictionaries as JSON lines to a file."""
        if not data_list:
            return
        with self.lock:
            with open(filepath, 'a', encoding='utf-8') as f:
                for item in data_list:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def append_professors(self, professors: 'List[Professor]'):
        dict_list = [p.model_dump(by_alias=True, exclude={"reviews"}) for p in professors]
        self._append_jsonl(self.prof_file, dict_list)

    def append_reviews(self, reviews: 'List[Rating]'):
        dict_list = [r.model_dump(by_alias=True) for r in reviews]
        self._append_jsonl(self.review_file, dict_list)

    def append_prof_attrs(self, prof_id: str, attrs: Dict[str, Any]):
        data = {"prof_id": prof_id}
        data.update(attrs)
        self._append_jsonl(self.attrs_file, [data])

    def get_failed_file_path(self) -> str:
        return os.path.join(self.base_dir, "failed_requests.json")

    def save_failed_request(self, payload: Dict[str, Any]):
        """
        Thread-safely appends a failed request payload to 'failed_requests.json'.
        """
        failed_file = self.get_failed_file_path()
        with self.lock:
            data = []
            if os.path.exists(failed_file):
                with open(failed_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        pass
            
            data.append(payload)
            
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    def load_all(self) -> Tuple[List[Professor], Dict[str, Any]]:
        """
        Loads all existing professors from jsonlines into objects, and sets `allReviewsScraped=True`
        if their ID is found in the attrs jsonlines.
        Returns the professors and an empty dict for metadata (as resultCount is no longer saved this way).
        """
        prof_map: Dict[str, Professor] = {}
        
        # 1. Load professors
        if os.path.exists(self.prof_file):
            with open(self.prof_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        prof = Professor(**data)
                        prof_map[prof.id] = prof
                    except Exception:
                        pass
                        
        # 2. Check attrs file for completed scrape tags
        if os.path.exists(self.attrs_file):
            seen_attr_ids = set()
            with open(self.attrs_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        pid = data.get("prof_id")
                        
                        # Apply attribute deduplication
                        if pid and pid in prof_map and pid not in seen_attr_ids:
                            if data.get("allReviewsScraped"):
                                prof_map[pid].all_reviews_scraped = True
                                seen_attr_ids.add(pid)
                    except Exception:
                        pass
                        
        return list(prof_map.values()), {}

    def get_failed_requests(self) -> List[Dict[str, Any]]:
        """
        Reads and returns the list of failed payloads.
        """
        failed_file = self.get_failed_file_path()
        with self.lock:
            if not os.path.exists(failed_file):
                return []
            with open(failed_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []

    def overwrite_failed_requests(self, payloads: List[Dict[str, Any]]):
        """
        Overwrites the failed requests file completely with a new list of payloads.
        Useful for un-queueing items that successfully retried.
        """
        failed_file = self.get_failed_file_path()
        with self.lock:
            if not payloads:
                if os.path.exists(failed_file):
                    os.remove(failed_file)
            else:
                with open(failed_file, 'w', encoding='utf-8') as f:
                    json.dump(payloads, f, indent=4, ensure_ascii=False)

    def correlate_data(self):
        """
        Synthesis method: loads all line-delimited items into memory, maps reviews to professors,
        and saves the final tree struct to `rmp_data.json`.
        It also rewrites the `rmp_review_data.json` and `rmp_prof_attrs.json` to prune duplicates.
        """
        print("Correlating split data files into the final rmp_data.json...")
        
        professors, _ = self.load_all()
        prof_map: Dict[str, Professor] = {p.id: p for p in professors}
        
        seen_review_ids = set()
        dedup_reviews = []
        
        # Pull reviews and attach to profs
        if os.path.exists(self.review_file):
            with open(self.review_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        r_data = json.loads(line)
                        r_id = r_data.get("id")
                        pid = r_data.get("prof_id")
                        
                        if pid and pid in prof_map and r_id not in seen_review_ids:
                            prof_map[pid].reviews.append(Rating(**r_data))
                            seen_review_ids.add(r_id)
                            dedup_reviews.append(r_data)
                    except Exception:
                        pass
        
        # Rewrite the split files without duplicates
        if dedup_reviews:
            self.lock.acquire()
            try:
                with open(self.review_file, 'w', encoding='utf-8') as f:
                    for item in dedup_reviews:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
            finally:
                self.lock.release()
                        
        # Compile final list
        output = {
            "professors": [p.model_dump(by_alias=True) for p in prof_map.values()]
        }
        
        with open(self.final_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        print(f"Done. Final output generated at {self.final_file}.")
