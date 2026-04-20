import os
from typing import Optional, List, Any

from .scrubbers.course_scrubber import CourseScrubber
from .scrubbers.rmp_scrubber import RmpScrubber
from .scrubbers.catalog_scrubber import CatalogScrubber
from .correlators.professor_correlator import ProfessorCorrelator


class DataFixingRunner:
    """Orchestrates the data scrubbing and professor correlation pipeline."""

    def __init__(self, root_dir: str):
        self._root_dir = root_dir

    def run(self) -> None:
        print("Beginning data preprocessing...")
        """Runs the complete data fixing pipeline."""
        paths = self._build_paths()
        course_data = self._run_course_scrubber(paths["courses_raw"], paths["courses_clean"])
        rmp_data = self._run_rmp_scrubber(paths["rmp_raw"], paths["rmp_clean"])
        catalog_data = self._run_catalog_scrubber(paths["catalog_raw"], paths["catalog_clean"])
        self._run_correlator(rmp_data, catalog_data, course_data, paths["prof_out"])
        print("Data preprocessing complete.")

    def _build_paths(self) -> dict:
        """Constructs all input/output paths relative to root_dir."""
        r = self._root_dir
        return {
            "courses_raw": os.path.join(r, "src", "knightrate", "course_scraping", "courses.json"),
            "rmp_raw": os.path.join(r, "src", "knightrate", "rmp_scraping", "rmp_data.json"),
            "catalog_raw": os.path.join(r, "src", "knightrate", "prof_scraping", "ucf_catalog_professors.json"),
            "courses_clean": os.path.join(r, "src", "knightrate", "data_fixing", "courses_cleaned.json"),
            "rmp_clean": os.path.join(r, "src", "knightrate", "data_fixing", "rmp_data_cleaned.json"),
            "catalog_clean": os.path.join(r, "src", "knightrate", "data_fixing", "ucf_catalog_professors_cleaned.json"),
            "prof_out": os.path.join(r, "src", "knightrate", "data_fixing", "professor_data.json"),
        }

    def _run_course_scrubber(self, raw_path: str, clean_path: str) -> Optional[List[Any]]:
        """Loads, scrubs, and saves course data."""
        print("Scrubbing UCF course catalog course data...")
        if not os.path.exists(raw_path):
            print(f"File {raw_path} not found, skipping course scrub.")
            return None
        scrubber = CourseScrubber()
        scrubber.load(raw_path)
        scrubber.scrub()
        scrubber.save(clean_path)
        data = scrubber.get_data()
        print("Finished.")
        return data

    def _run_rmp_scrubber(self, raw_path: str, clean_path: str) -> Optional[List[Any]]:
        """Loads, scrubs, and saves RMP data."""
        print("Scrubbing RMP data...")
        if not os.path.exists(raw_path):
            print(f"File {raw_path} not found, skipping RMP scrub.")
            return None
        scrubber = RmpScrubber()
        scrubber.load(raw_path)
        scrubber.scrub()
        scrubber.save(clean_path)
        data = scrubber.get_data()
        print("Finished.")
        return data

    def _run_catalog_scrubber(self, raw_path: str, clean_path: str) -> Optional[List[Any]]:
        """Loads, scrubs, and saves catalog data."""
        print("Scrubbing UCF course catalog professor data...")
        if not os.path.exists(raw_path):
            print(f"File {raw_path} not found, skipping Catalog scrub.")
            return None
        scrubber = CatalogScrubber()
        scrubber.load(raw_path)
        scrubber.scrub()
        scrubber.save(clean_path)
        data = scrubber.get_data()
        print("Finished.")
        return data

    def _run_correlator(
        self, rmp_data: Any, catalog_data: Any, courses_data: Any, out_path: str
    ) -> None:
        """Correlates professor data from RMP and catalog sources."""
        print("Correlating all data...")
        if rmp_data is None or catalog_data is None:
            print("Missing data required for correlation, skipping.")
            return
        correlator = ProfessorCorrelator()
        correlator.correlate(rmp_data, catalog_data, courses_data)
        correlator.save(out_path)
        print("Finished.")
