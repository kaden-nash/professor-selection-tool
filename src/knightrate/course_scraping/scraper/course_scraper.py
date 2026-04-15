from urllib.parse import urljoin
from tqdm import tqdm
from scraper.html_fetcher import HtmlFetcher
from scraper.parser import Parser

class CourseScraper:
    """Orchestrates fetching and parsing of catalog course data."""

    def __init__(self, fetcher: HtmlFetcher, parser: Parser):
        self.fetcher = fetcher
        self.parser = parser

    def run_scraping(self, root_url: str) -> list[str]:
        """Runs the entire scraping process and returns course titles."""
        root_html = self.fetcher.fetch_html(root_url)
        group_links = self.parser.extract_group_links(root_html)

        all_courses = []
        
        for link in tqdm(group_links, desc="Scraping Subject Groups"):
            full_url = urljoin(root_url, link)
            try:
                page_html = self.fetcher.fetch_html(full_url)
                titles = self.parser.extract_course_titles(page_html)
                all_courses.extend(titles)
            except Exception as e:
                print(f"Error fetching {full_url}: {e}")

        return all_courses
