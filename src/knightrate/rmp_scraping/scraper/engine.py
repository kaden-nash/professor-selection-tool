import concurrent.futures
from typing import List, Dict, Any, Optional
import copy
from .client import GraphQLClient, GraphQLRequestError  
from .parser import parse_professors, parse_ratings  
from .models import Professor
from .monitor import Monitor  
from .storage import DataStorage  

PROFESSOR_QUERY_DICT: Dict[str, Any] = {
    "query": "query TeacherSearchPaginationQuery(\n  $count: Int!\n  $cursor: String\n  $query: TeacherSearchQuery!\n) {\n  search: newSearch {\n    teachers(query: $query, first: $count, after: $cursor) {\n      didFallback\n      edges {\n        cursor\n        node {\n          id\n          legacyId\n          avgRating\n          numRatings\n          wouldTakeAgainPercent\n          avgDifficulty\n          department\n          school {\n            name\n            id\n          }\n          firstName\n          lastName\n          isSaved\n          __typename\n        }\n      }\n      pageInfo {\n        hasNextPage\n        endCursor\n      }\n      resultCount\n      filters {\n        field\n        options {\n          value\n          id\n        }\n      }\n    }\n  }\n}",
    "operationName": "TeacherSearchPaginationQuery",
    "variables": {"count": 5, "cursor": "YXJyYXljb25uZWN0aW9uOjE5", "query": {"text": "", "schoolID": "U2Nob29sLTEwODI=", "fallback": True}}
}

RATINGS_QUERY_DICT: Dict[str, Any] = {
    "query": "query RatingsListQuery(\n  $count: Int!\n  $id: ID!\n  $courseFilter: String\n  $cursor: String\n) {\n  node(id: $id) {\n    __typename\n    ... on Teacher {\n      ...RatingsList_teacher_4pguUW\n    }\n    id\n  }\n}\n\nfragment CourseMeta_rating on Rating {\n  attendanceMandatory\n  wouldTakeAgain\n  grade\n  textbookUse\n  isForOnlineClass\n  isForCredit\n}\n\nfragment NoRatingsArea_teacher on Teacher {\n  lastName\n  ...RateTeacherLink_teacher\n}\n\nfragment ProfessorNoteEditor_rating on Rating {\n  id\n  legacyId\n  class\n  teacherNote {\n    id\n    teacherId\n    comment\n  }\n}\n\nfragment ProfessorNoteEditor_teacher on Teacher {\n  id\n}\n\nfragment ProfessorNoteFooter_note on TeacherNotes {\n  legacyId\n  flagStatus\n}\n\nfragment ProfessorNoteFooter_teacher on Teacher {\n  legacyId\n  isProfCurrentUser\n}\n\nfragment ProfessorNoteHeader_note on TeacherNotes {\n  createdAt\n  updatedAt\n}\n\nfragment ProfessorNoteHeader_teacher on Teacher {\n  lastName\n}\n\nfragment ProfessorNoteSection_rating on Rating {\n  teacherNote {\n    ...ProfessorNote_note\n    id\n  }\n  ...ProfessorNoteEditor_rating\n}\n\nfragment ProfessorNoteSection_teacher on Teacher {\n  ...ProfessorNote_teacher\n  ...ProfessorNoteEditor_teacher\n}\n\nfragment ProfessorNote_note on TeacherNotes {\n  comment\n  ...ProfessorNoteHeader_note\n  ...ProfessorNoteFooter_note\n}\n\nfragment ProfessorNote_teacher on Teacher {\n  ...ProfessorNoteHeader_teacher\n  ...ProfessorNoteFooter_teacher\n}\n\nfragment RateTeacherLink_teacher on Teacher {\n  legacyId\n  numRatings\n  lockStatus\n}\n\nfragment RatingFooter_rating on Rating {\n  id\n  comment\n  adminReviewedAt\n  flagStatus\n  legacyId\n  thumbsUpTotal\n  thumbsDownTotal\n  thumbs {\n    thumbsUp\n    thumbsDown\n    computerId\n    id\n  }\n  teacherNote {\n    id\n  }\n  ...Thumbs_rating\n}\n\nfragment RatingFooter_teacher on Teacher {\n  id\n  legacyId\n  lockStatus\n  isProfCurrentUser\n  ...Thumbs_teacher\n}\n\nfragment RatingHeader_rating on Rating {\n  legacyId\n  date\n  class\n  helpfulRating\n  clarityRating\n  isForOnlineClass\n}\n\nfragment RatingSuperHeader_rating on Rating {\n  legacyId\n}\n\nfragment RatingSuperHeader_teacher on Teacher {\n  firstName\n  lastName\n  legacyId\n  school {\n    name\n    id\n  }\n}\n\nfragment RatingTags_rating on Rating {\n  ratingTags\n}\n\nfragment RatingValues_rating on Rating {\n  helpfulRating\n  clarityRating\n  difficultyRating\n}\n\nfragment Rating_rating on Rating {\n  comment\n  flagStatus\n  createdByUser\n  teacherNote {\n    id\n  }\n  ...RatingHeader_rating\n  ...RatingSuperHeader_rating\n  ...RatingValues_rating\n  ...CourseMeta_rating\n  ...RatingTags_rating\n  ...RatingFooter_rating\n  ...ProfessorNoteSection_rating\n}\n\nfragment Rating_teacher on Teacher {\n  ...RatingFooter_teacher\n  ...RatingSuperHeader_teacher\n  ...ProfessorNoteSection_teacher\n}\n\nfragment RatingsList_teacher_4pguUW on Teacher {\n  id\n  legacyId\n  lastName\n  numRatings\n  school {\n    id\n    legacyId\n    name\n    city\n    state\n    avgRating\n    numRatings\n  }\n  ...Rating_teacher\n  ...NoRatingsArea_teacher\n  ratings(first: $count, after: $cursor, courseFilter: $courseFilter) {\n    edges {\n      cursor\n      node {\n        ...Rating_rating\n        id\n        __typename\n      }\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}\n\nfragment Thumbs_rating on Rating {\n  id\n  comment\n  adminReviewedAt\n  flagStatus\n  legacyId\n  thumbsUpTotal\n  thumbsDownTotal\n  thumbs {\n    computerId\n    thumbsUp\n    thumbsDown\n    id\n  }\n  teacherNote {\n    id\n  }\n}\n\nfragment Thumbs_teacher on Teacher {\n  id\n  legacyId\n  lockStatus\n  isProfCurrentUser\n}\n",
    "operationName": "RatingsListQuery",
    "variables": {"count": 5, "id": "", "courseFilter": None, "cursor": ""}
}

class ScraperEngine:
    def __init__(self, client: GraphQLClient, storage: DataStorage, monitor: Monitor, limit_professors: Optional[int] = None, limit_reviews: Optional[int] = None):
        self.client = client
        self.storage = storage
        self.monitor = monitor
        self.limit_professors = limit_professors
        self.limit_reviews = limit_reviews
        self.result_count = 0
        self._completed_professors = 0
        self._professors_ref: List[Professor] = []
        self._prof_map_ref: Dict[str, Professor] = {}
        self._is_cancelled = False
        self.executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self.futures: List[Any] = []
        
    def fetch_all_professors(self) -> List[Professor]:
        # Attempt to load existing data to resume
        existing_profs, metadata = self.storage.load_all()
        # We put existing into a dict keyed by ID for faster duplicate checking
        # and so we can preserve their already-downloaded reviews
        prof_map = {p.id: p for p in existing_profs}
        
        # Keep a persistent set of seen IDs for duplication checking
        seen_prof_ids = set(prof_map.keys())
        # Buffer only for newly scraped professors to write to file
        professors_buffer: list[Professor] = []
        
        # Track total scraped to adhere to limit_professors correctly
        total_profs_count: int = len(seen_prof_ids)
        
        cursor = "YXJyYXljb25uZWN0aW9uOi0x"
        has_next_page = True
        
        # We fetch chunk size = 5
        variables = copy.deepcopy(PROFESSOR_QUERY_DICT["variables"])
        variables["count"] = 5
        
        first_req = True
        
        limit_prof = self.limit_professors
        while has_next_page:
            variables["cursor"] = cursor
            try:
                data = self.client.execute(PROFESSOR_QUERY_DICT["query"], variables, "TeacherSearchPaginationQuery")
                
                profs, page_info, count = parse_professors(data)
                
                if limit_prof is not None:
                    remaining = limit_prof - total_profs_count  
                    profs = profs[:remaining]
                    
                for p in profs:
                    if p.id not in seen_prof_ids:
                        seen_prof_ids.add(p.id)
                        professors_buffer.append(p)
                        total_profs_count += 1 
                
                if first_req:
                    if limit_prof is None:
                        self.result_count = count
                    else:
                        self.result_count = min(count, limit_prof)  
                    self.monitor.init_professors(self.result_count)
                    # We might have already loaded a bunch from JSON.
                    # Fast-forward the progress bar to show what we already have
                    if total_profs_count > 0:
                        self.monitor.update_professors(min(total_profs_count, self.result_count))
                    first_req = False
                    
                cursor = page_info.get("endCursor", "")
                has_next_page = page_info.get("hasNextPage", False)
                
                # Only increment the bar by however many NEW professors we actually added this loop
                added_this_loop = len(professors_buffer) - (len(professors_buffer) - sum(1 for p in profs if p in professors_buffer))
                if added_this_loop > 0:
                     self.monitor.update_professors(added_this_loop)
                
                # Since the API might be flaky, break out if has_next_page is False or empty cursor
                if not has_next_page or not cursor:
                    break
                    
                if limit_prof is not None:
                    if total_profs_count >= limit_prof:  
                        break
            except GraphQLRequestError as e:
                print(f"Failed to fetch professors chunk: {e.last_error}")
                self.storage.save_failed_request(e.payload)
                break
            except Exception as e:
                print(f"Unexpected error fetching professors: {e}")
                break
            
            # Buffer flush
            if len(professors_buffer) >= 50:
                self.storage.append_professors(professors_buffer)
                professors_buffer.clear()
                
        # Final buffer flush
        if professors_buffer:
            self.storage.append_professors(professors_buffer)
            professors_buffer.clear()
            
        print("Professor phase complete. Loading stored indexes...")
        return self.storage.load_all()[0]

    def fetch_reviews_for_professor(self, prof: Professor):
        if getattr(self, "_is_cancelled", False):
            return
            
        # Skip if they have no ratings
        if prof.num_ratings == 0:
            self.monitor.update_reviews(1)
            self.storage.append_prof_attrs(prof.id, {"allReviewsScraped": True})
            with self.storage.lock:
                self._completed_professors += 1
            return
            
        # Skip if we already scraped their reviews in a previous interrupted run
        if prof.all_reviews_scraped:
            self.monitor.update_reviews(1)
            with self.storage.lock:
                self._completed_professors += 1
            return
            
        cursor = "YXJyYXljb25uZWN0aW9uOi0x"
        has_next_page = True
        seen_review_ids = set()
        reviews_buffer = []
        
        variables = copy.deepcopy(RATINGS_QUERY_DICT["variables"])
        variables["count"] = 5
        variables["id"] = prof.id
        
        limit_rev = self.limit_reviews
        total_scraped_this_run = int(0)
        
        while has_next_page:
            variables["cursor"] = cursor
            
            try:
                data = self.client.execute(RATINGS_QUERY_DICT["query"], variables, "RatingsListQuery")
                ratings, page_info = parse_ratings(data)
                
                if limit_rev is not None:
                    remaining = limit_rev - total_scraped_this_run  
                    ratings = ratings[:remaining]
                    
                for r in ratings:
                    if r.id not in seen_review_ids:
                        seen_review_ids.add(r.id)
                        r.prof_id = prof.id
                        reviews_buffer.append(r)
                        total_scraped_this_run = int(total_scraped_this_run) + 1    
                        
                if len(reviews_buffer) >= 50:
                    self.storage.append_reviews(reviews_buffer)
                    reviews_buffer.clear()
                
                cursor = page_info.get("endCursor", "")
                has_next_page = page_info.get("hasNextPage", False)
                
                if not has_next_page or not cursor:
                    break
                    
                if limit_rev is not None:
                    if total_scraped_this_run >= limit_rev:  
                        break
            except GraphQLRequestError as e:
                print(f"Failed to fetch reviews for professor {prof.id}: {e.last_error}")
                self.storage.save_failed_request(e.payload)
                break
            except Exception as e:
                print(f"Unexpected fault while fetching reviews for professor {prof.id}: {e}")
                break
                
        if reviews_buffer:
            self.storage.append_reviews(reviews_buffer)
            reviews_buffer.clear()
            
        # Write completion flag if scraping didn't get cancelled via limit
        if has_next_page is False or not cursor:
            self.storage.append_prof_attrs(prof.id, {"allReviewsScraped": True})
            
        self.monitor.update_reviews(1)
        
        with self.storage.lock:
            self._completed_professors += 1

    def run(self):
        print("Scraping started. Fetching all professors in UCF...")
        professors = self.fetch_all_professors()
        
        # Prepare auto-save global references for the threads
        self._professors_ref = professors
        self._prof_map_ref = {p.id: p for p in self._professors_ref}
        self._completed_professors = 0
        
        print(f"Fetched {len(professors)} professors. Now fetching reviews...")
        self.monitor.init_reviews(len(professors))
        
        self._is_cancelled = False
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=200)
        self.futures = [self.executor.submit(self.fetch_reviews_for_professor, p) for p in self._professors_ref]  
        for future in concurrent.futures.as_completed(self.futures):
            future.result()
            
        _executor = self.executor
        _executor.shutdown(wait=True)
            
        self.monitor.close()
        
        print("Exporting data to JSON storage...")
        self.storage.correlate_data()

    def run_reviews_only(self):
        print("Running in --reviews-only mode. Checking local JSON database...")
        existing_profs, metadata = self.storage.load_all()
        
        if not existing_profs:
            print("[!] No existing professors found in the local database. Please run --all first to build the professor dataset.")
            return
            
        self.result_count = metadata.get("resultCount", len(existing_profs))
        
        # Prepare auto-save global references
        self._professors_ref = existing_profs  
        self._prof_map_ref = {p.id: p for p in self._professors_ref}
        self._completed_professors = 0
        
        print(f"Loaded {len(existing_profs)} professors from JSON.")
        
        professors_to_process = self._professors_ref
        limit_prof = self.limit_professors
        if limit_prof is not None:
            professors_to_process = self._professors_ref[:limit_prof]  
            print(f"Applying limit: Only fetching reviews for the first {limit_prof} professors.")
            
        print(f"Fetching reviews...")
        self.monitor.init_reviews(len(professors_to_process))
        
        self._is_cancelled = False
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=200)
        self.futures = [self.executor.submit(self.fetch_reviews_for_professor, p) for p in professors_to_process]  
        for future in concurrent.futures.as_completed(self.futures):
            future.result()
            
        _executor = self.executor
        _executor.shutdown(wait=True)
            
        self.monitor.close()
        print("Exporting finalized data to JSON storage...")
        self.storage.correlate_data()

    def retry_failed_requests(self):
        failed_payloads = self.storage.get_failed_requests()
        if not failed_payloads:
            return
            
        print(f"Loading existing data to merge {len(failed_payloads)} retried requests...")
        professors, metadata = self.storage.load_all()
        if not professors:
            print("Warning: No existing ucf_professors_data.json found. Retries won't find existing professor nodes.")
            
        prof_map = {p.id: p for p in professors}
        still_failed = []
        
        self.monitor.init_professors(len(failed_payloads))
        
        for payload in failed_payloads:
            op_name = payload.get("operationName", "Unknown")
            try:
                data = self.client.execute(payload["query"], payload["variables"], op_name)
                
                if op_name == "TeacherSearchPaginationQuery":
                    profs, _, _ = parse_professors(data)
                    for p in profs:
                        if p.id not in prof_map:
                            professors.append(p)
                            prof_map[p.id] = p
                elif op_name == "RatingsListQuery":
                    ratings, _ = parse_ratings(data)
                    prof_id = payload["variables"].get("id")
                    if prof_id in prof_map:
                        prof_map[prof_id].reviews.extend(ratings)
                    else:
                        print(f"Warning: Fetched reviews for unknown professor {prof_id}. Start scraping from scratch and get all professors again.")
            except GraphQLRequestError as e:
                print(f"Retry failed again for {op_name}: {e.last_error}")
                still_failed.append(e.payload)
            except Exception as e:
                print(f"Unexpected error during retry of {op_name}: {e}")
                still_failed.append(payload)
                
            self.monitor.update_professors(1)
            
        self.monitor.close()
        
        print("Saving merged results to JSON storage...")
        self.storage.save_all(professors, context_data=metadata)
        
        if still_failed:
            print(f"{len(still_failed)} requests failed again. Saving back to queue.")
            self.storage.overwrite_failed_requests(still_failed)
        else:
            print("All failed requests successfully retried and merged!")
            self.storage.overwrite_failed_requests([])
