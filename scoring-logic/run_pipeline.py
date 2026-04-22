"""
run_pipeline.py — Master orchestration script for the UCF Professor Scraper pipeline.

Usage:
    python run_pipeline.py [options]

Run `python run_pipeline.py --help` for full option descriptions.
"""
import argparse
import traceback
from dataclasses import dataclass
from typing import Optional

from knightrate.course_scraping.course_scrape_runner import CourseScrapeRunner
from knightrate.prof_scraping.prof_scrape_runner import ProfScrapeRunner
from knightrate.rmp_scraping.rmp_scrape_runner import RmpScrapeRunner
from knightrate.rmp_scraping.rmp_scrape_runner import ScraperArgs
from knightrate.data_fixing.data_fixing_runner import DataFixingRunner
from knightrate.professor_scoring.professor_scoring_runner import ProfessorScoringRunner
from knightrate.output_paths import create_output_dirs, RMP_SCRAPING_OUTPUT_DIR, COURSE_SCRAPING_OUTPUT_DIR, PROF_SCRAPING_OUTPUT_DIR
from knightrate.output_paths import RMP_REVIEW_DATA_PATH, RMP_PROF_DATA_PATH, RMP_PROF_ATTRS_PATH, FAILED_REQUEST_PATH, COURSES_PATH, CATALOG_PROFESSORS_PATH


@dataclass
class PipelineConfig:
    """All configuration flags for the pipeline orchestrator."""
    # Orchestration
    scrape_rmp: bool = False
    scrape_profs: bool = False
    scrape_courses: bool = False
    skip_fix: bool = False
    skip_scoring: bool = False

    # RMP Scraping
    reviews_only: bool = False
    limit_profs: int | None = None
    limit_reviews_per_prof: int | None = None
    clean_scrape: bool = False

@dataclass
class StageResult:
    """Records the outcome of a single pipeline stage."""
    stage_name: str
    success: bool
    error: Optional[str] = None


class PipelineRunner:
    """Orchestrates all pipeline stages in the correct order."""

    def __init__(self, config: PipelineConfig):
        self._config = config
        self._results: list[StageResult] = []

    def run(self) -> None:
        """Executes enabled pipeline stages and prints a summary."""
        create_output_dirs()

        if self._config.clean_scrape:
            self._wipe_scraping_files()

        self._run_optional_stages()
        self._run_required_stages()
        self._print_summary()

    def _run_optional_stages(self) -> None:
        """Runs the network-bound scraping stages when opted in."""
        scraper_args = ScraperArgs(self._config.reviews_only, self._config.limit_profs, self._config.limit_reviews_per_prof)
        if self._config.scrape_rmp:
            self._execute("RMP Scraping", self._build_rmp_runner(scraper_args))
        if self._config.scrape_profs:
            self._execute("Prof Scraping", self._build_prof_runner())
        if self._config.scrape_courses:
            self._execute("Course Scraping", self._build_course_runner())

    def _run_required_stages(self) -> None:
        """Runs the data-fixing and scoring stages unless skipped."""
        if not self._config.skip_fix:
            self._execute("Data Fixing", DataFixingRunner())
        if not self._config.skip_scoring:
            self._execute("Professor Scoring", ProfessorScoringRunner())

    def _execute(self, name: str, runner) -> None:
        """Runs a single stage, capturing any exception as a StageResult."""
        print(f"\n{'=' * 60}")
        print(f"  Stage: {name}")
        print(f"{'=' * 60}")
        try:
            runner.run()
            self._results.append(StageResult(stage_name=name, success=True))
        except Exception:
            error_text = traceback.format_exc()
            print(f"[!] Stage '{name}' failed:\n{error_text}")
            self._results.append(StageResult(stage_name=name, success=False, error=error_text))

    def _print_summary(self) -> None:
        """Prints a human-readable summary table of all stage results."""
        print(f"\n{'=' * 60}")
        print("  Pipeline Summary")
        print(f"{'=' * 60}")
        for result in self._results:
            status = "✓ PASS" if result.success else "✗ FAIL"
            print(f"  {status}  {result.stage_name}")
        print(f"{'=' * 60}\n")

    def _build_rmp_runner(self, scraper_args: ScraperArgs) -> RmpScrapeRunner:
        return RmpScrapeRunner(RMP_SCRAPING_OUTPUT_DIR, scraper_args)

    def _build_prof_runner(self) -> ProfScrapeRunner:
        return ProfScrapeRunner(PROF_SCRAPING_OUTPUT_DIR)

    def _build_course_runner(self) -> CourseScrapeRunner:
        return CourseScrapeRunner(COURSE_SCRAPING_OUTPUT_DIR)

    def _wipe_scraping_files(self) -> None:
        """Truncates all incremental scraper output files to prepare for a clean run."""
        for path in (
            RMP_REVIEW_DATA_PATH,
            RMP_PROF_ATTRS_PATH,
            RMP_PROF_DATA_PATH,
            FAILED_REQUEST_PATH,
            CATALOG_PROFESSORS_PATH,
            COURSES_PATH,
        ):
            with open(path, "w"):
                pass

def _parse_args() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="run_pipeline.py",
        description="UCF Professor Scraper — master pipeline orchestrator",
    )
    parser.add_argument(
        "--scrape-rmp",
        action="store_true",
        help="Run the RateMyProfessors scraping stage (long-running, network-bound).",
    )
    parser.add_argument(
        "--scrape-profs",
        action="store_true",
        help="Run the UCF catalog professor scraping stage (long-running, network-bound).",
    )
    parser.add_argument(
        "--scrape-courses",
        action="store_true",
        help="Run the UCF course catalog scraping stage.",
    )
    parser.add_argument(
        "--skip-fix",
        action="store_true",
        help="Skip the data-fixing / correlation stage.",
    )
    parser.add_argument(
        "--skip-scoring",
        action="store_true",
        help="Skip the professor scoring stage.",
    )
    parser.add_argument(
        "--reviews-only",
        action="store_true",
        help="Specifies that RMP scraping should only scrape reviews and not professors. Only applies if --scrape-rmp is also used."
    )
    parser.add_argument(
        "--limit-profs",
        type=int,
        help="Sets a limit on the amount of professors to scrape. Only applies if --scrape-rmp is also used."
    )
    parser.add_argument(
        "--limit-reviews",
        type=int,
        help="Sets a limit on the amount of reviews to scrape per professor. Only applies if --scrape-rmp is also used."
    )
    parser.add_argument(
        "--clean-scrape",
        action="store_true",
        help="Clears every output file used by the RMP scraper for a fresh run."
        )
    return parser.parse_args()


def _build_config(args: argparse.Namespace) -> PipelineConfig:
    """Constructs a PipelineConfig from parsed CLI arguments."""
    return PipelineConfig(
        scrape_rmp=args.scrape_rmp,
        scrape_profs=args.scrape_profs,
        scrape_courses=args.scrape_courses,
        skip_fix=args.skip_fix,
        skip_scoring=args.skip_scoring,
        reviews_only=args.reviews_only,
        limit_profs=args.limit_profs,
        limit_reviews_per_prof=args.limit_reviews,
        clean_scrape=args.clean_scrape
    )


def main() -> None:
    """Entry point for the pipeline orchestrator."""
    args = _parse_args()
    config = _build_config(args)
    PipelineRunner(config).run()


if __name__ == "__main__":
    main()
