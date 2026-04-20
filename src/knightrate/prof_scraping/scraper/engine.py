from dataclasses import dataclass
from typing import List

from .client import CatalogClient
from .parser import CatalogParser
from .storage import DataStorage


@dataclass
class ScraperDependencies:
    """Bundles all collaborators needed by ScraperEngine."""
    client: CatalogClient
    parser: CatalogParser
    storage: DataStorage


class ScraperEngine:
    """Orchestrates the end-to-end catalog scrape."""

    def __init__(self, deps: ScraperDependencies):
        self._deps = deps

    def run(self) -> None:
        """Fetch, parse, and persist all professor entries."""
        html = self._fetch_html()
        entries = self._parse_entries(html)
        self._save_entries(entries)
        print(f"Done. {len(entries)} professor entries saved to "
              f"{self._deps.storage.output_path}")

    def _fetch_html(self) -> str:
        """Fetch rendered HTML from the UCF catalog page."""
        print("Fetching UCF catalog page...")
        html = self._deps.client.fetch_html()
        print("Got UCF catalog page.")
        return html

    def _parse_entries(self, html: str) -> List[str]:
        """Parse professor entries from the rendered HTML."""
        print("Parsing professor entries...")
        entries = self._deps.parser.parse(html)
        print("Finished parsing.")
        return entries

    def _save_entries(self, entries: List[str]) -> None:
        """Persist professor entries via storage."""
        print("Saving results...")
        self._deps.storage.save(entries)
        print("Finished saving results.")
