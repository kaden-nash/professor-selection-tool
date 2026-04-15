import os
import signal
import sys

from prof_scraping.scraper.client import CatalogClient
from prof_scraping.scraper.parser import CatalogParser
from prof_scraping.scraper.storage import DataStorage
from prof_scraping.scraper.monitor import Monitor
from prof_scraping.scraper.engine import ScraperEngine, ScraperDependencies


class ProfScrapeRunner:
    """Orchestrates the UCF professor catalog scraping pipeline."""

    def __init__(self, output_dir: str):
        self._output_dir = output_dir

    def run(self) -> None:
        """Runs the full professor catalog scraping pipeline."""
        engine, monitor = self._build_engine()
        self._setup_signal_handler(monitor)
        try:
            engine.run()
        except Exception as exc:
            print(f"\n[!] An error occurred: {exc}")
            monitor.close()
            sys.exit(1)

    def _build_engine(self) -> tuple:
        """Wires up all scraper components."""
        client = CatalogClient()
        parser = CatalogParser()
        storage = DataStorage(self._output_dir)
        monitor = Monitor()
        deps = ScraperDependencies(
            client=client,
            parser=parser,
            storage=storage,
            monitor=monitor,
        )
        return ScraperEngine(deps), monitor

    def _setup_signal_handler(self, monitor: Monitor) -> None:
        """Registers SIGINT handler to close the progress bar on Ctrl+C."""
        def handler(sig, frame):
            print("\n[!] Scrape interrupted by user.")
            monitor.close()
            sys.exit(1)
        signal.signal(signal.SIGINT, handler)
