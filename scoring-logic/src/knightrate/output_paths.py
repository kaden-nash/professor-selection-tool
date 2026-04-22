from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = _SRC_DIR / "output_files"
RMP_SCRAPING_OUTPUT_DIR = OUTPUT_DIR / "rmp_scraping"
PROFESSOR_SCORING_OUTPUT_DIR = OUTPUT_DIR / "professor_scoring"
PROF_SCRAPING_OUTPUT_DIR = OUTPUT_DIR / "prof_scraping"
DATA_FIXING_OUTPUT_DIR = OUTPUT_DIR / "data_fixing"
COURSE_SCRAPING_OUTPUT_DIR = OUTPUT_DIR / "course_scraping"

# RMP Paths
FAILED_REQUEST_PATH = RMP_SCRAPING_OUTPUT_DIR / "failed_requests.json"
RMP_DATA_PATH = RMP_SCRAPING_OUTPUT_DIR / "rmp_data.json"
RMP_PROF_ATTRS_PATH = RMP_SCRAPING_OUTPUT_DIR / "rmp_prof_attrs.json"
RMP_PROF_DATA_PATH = RMP_SCRAPING_OUTPUT_DIR / "rmp_prof_data.json"
RMP_REVIEW_DATA_PATH = RMP_SCRAPING_OUTPUT_DIR / "rmp_review_data.json"

# Professor Scoring Paths
GLOBAL_STATISTICS_PATH = PROFESSOR_SCORING_OUTPUT_DIR / "global_statistics.json"
PROFESSOR_RATINGS_PATH = PROFESSOR_SCORING_OUTPUT_DIR / "professor_ratings.json"

# Professor Scraping Paths
CATALOG_PROFESSORS_PATH = PROF_SCRAPING_OUTPUT_DIR / "catalog_professors.json"

# Data Fixing Paths
COURSES_CLEANED_PATH = DATA_FIXING_OUTPUT_DIR / "courses_cleaned.json"
PROFESSOR_DATA_PATH = DATA_FIXING_OUTPUT_DIR / "professor_data.json"
RMP_DATA_CLEANED_PATH = DATA_FIXING_OUTPUT_DIR / "rmp_data_cleaned.json"
CATALOG_PROFESSORS_CLEANED_PATH = DATA_FIXING_OUTPUT_DIR / "catalog_professors_cleaned.json"

# Course Scraping Paths
COURSES_PATH = COURSE_SCRAPING_OUTPUT_DIR / "courses.json"

def create_output_dirs():
    """
    Call this once at the start of your program execution
    to create the necessary directory hierarchy.
    """
    RMP_SCRAPING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROFESSOR_SCORING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROF_SCRAPING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FIXING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    COURSE_SCRAPING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)