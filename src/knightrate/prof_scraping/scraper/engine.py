from dataclasses import dataclass
from typing import List

from scraper.client import CatalogClient
from scraper.parser import CatalogParser
from scraper.storage import DataStorage
from scraper.monitor import Monitor


@dataclass
class ScraperDependencies:
    """Bundles all collaborators needed by ScraperEngine."""
    client: CatalogClient
    parser: CatalogParser
    storage: DataStorage
    monitor: Monitor


class ScraperEngine:
    """Orchestrates the end-to-end catalog scrape."""

    def __init__(self, deps: ScraperDependencies):
        self._deps = deps

    def run(self) -> None:
        """Fetch, parse, monitor, and persist all professor entries."""
        html = self._fetch_html()
        entries = self._parse_entries(html)
        self._report_progress(len(entries))
        self._save_entries(entries)
        self._deps.monitor.close()
        print(f"Done. {len(entries)} professor entries saved to "
              f"{self._deps.storage.output_path}")

    def _fetch_html(self) -> str:
        """Fetch rendered HTML from the UCF catalog page."""
        print("Fetching UCF catalog page...")
        return self._deps.client.fetch_html()

    def _parse_entries(self, html: str) -> List[str]:
        """Parse professor entries from the rendered HTML."""
        print("Parsing professor entries...")
        return self._deps.parser.parse(html)

    def _report_progress(self, total: int) -> None:
        """Initialise and immediately complete the progress bar."""
        self._deps.monitor.init(total)
        self._deps.monitor.update(total)

    def _save_entries(self, entries: List[str]) -> None:
        """Persist professor entries via storage."""
        print("Saving results...")
        self._deps.storage.save(entries)
