import os
from typing import Optional, List, Any
from pathlib import Path

from .scrubbers.course_scrubber import CourseScrubber
from .scrubbers.rmp_scrubber import RmpScrubber
from .scrubbers.catalog_scrubber import CatalogScrubber
from .correlators.professor_correlator import ProfessorCorrelator
from ..output_paths import COURSES_PATH, COURSES_CLEANED_PATH, CATALOG_PROFESSORS_PATH,CATALOG_PROFESSORS_CLEANED_PATH, RMP_DATA_PATH, RMP_DATA_CLEANED_PATH, PROFESSOR_DATA_PATH


class DataFixingRunner:
    """Orchestrates the data scrubbing and professor correlation pipeline."""

    def __init__(self):
        pass

    def run(self) -> None:
        "Manages scrubbing and correlation."
        print("Beginning data preprocessing...")
        """Runs the complete data fixing pipeline."""
        course_data = self._run_course_scrubber(COURSES_PATH, COURSES_CLEANED_PATH)
        rmp_data = self._run_rmp_scrubber(RMP_DATA_PATH, RMP_DATA_CLEANED_PATH)
        catalog_data = self._run_catalog_scrubber(CATALOG_PROFESSORS_PATH, CATALOG_PROFESSORS_CLEANED_PATH)
        self._run_correlator(rmp_data, catalog_data, course_data, PROFESSOR_DATA_PATH)
        print("Data preprocessing complete.")

    def _run_course_scrubber(self, raw_path: Path, clean_path: Path) -> Optional[List[Any]]:
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

    def _run_rmp_scrubber(self, raw_path: Path, clean_path: Path) -> Optional[List[Any]]:
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

    def _run_catalog_scrubber(self, raw_path: Path, clean_path: Path) -> Optional[List[Any]]:
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
        self, rmp_data: Any, catalog_data: Any, courses_data: Any, out_path: Path
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
