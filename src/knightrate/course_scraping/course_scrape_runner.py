from .scraper.html_fetcher import HtmlFetcher
from .scraper.parser import Parser
from .scraper.course_scraper import CourseScraper
from .storage.data_storage import DataStorage

ROOT_URL = "https://www.ucf.edu/catalog/undergraduate/#/courses"


class CourseScrapeRunner:
    """Orchestrates the UCF course scraping pipeline."""

    def __init__(self, output_dir: str):
        self._output_dir = output_dir

    def run(self) -> None:
        """Runs the full course scraping pipeline."""
        print(f"Starting UCF Course Scraper on {ROOT_URL}")
        fetcher = HtmlFetcher()
        try:
            courses = self._scrape(fetcher)
            self._persist(courses)
        finally:
            fetcher.close()

    def _scrape(self, fetcher: HtmlFetcher) -> list:
        """Delegates scraping to CourseScraper and returns results."""
        print("Fetching and processing html...")
        parser = Parser()
        scraper = CourseScraper(fetcher, parser)
        courses = scraper.run_scraping(ROOT_URL)
        print("Finished fetching and processing html.")
        return courses

    def _persist(self, courses: list) -> None:
        """Saves scraped courses to the output directory."""
        storage = DataStorage(self._output_dir)
        if courses:
            storage.save_courses(courses)
            print(f"Successfully saved {len(courses)} courses.")
        else:
            print("Finished scraping but no courses were found.")
