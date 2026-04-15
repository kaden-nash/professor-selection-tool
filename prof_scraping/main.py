import os
import signal
import sys
import argparse

from scraper.client import CatalogClient
from scraper.parser import CatalogParser
from scraper.storage import DataStorage
from scraper.monitor import Monitor
from scraper.engine import ScraperEngine, ScraperDependencies


def _build_engine() -> tuple[ScraperEngine, Monitor]:
    """Wire up all scraper components from the filesystem."""
    client = CatalogClient()
    parser = CatalogParser()
    output_dir = os.path.dirname(os.path.abspath(__file__))
    storage = DataStorage(output_dir)
    monitor = Monitor()
    deps = ScraperDependencies(
        client=client,
        parser=parser,
        storage=storage,
        monitor=monitor,
    )
    return (ScraperEngine(deps), monitor)


def _setup_signal_handler(monitor: Monitor) -> None:
    """Register SIGINT handler to close the progress bar on Ctrl+C."""
    def handler(sig, frame):
        print("\n[!] Scrape interrupted by user.")
        monitor.close()
        sys.exit(1)
    signal.signal(signal.SIGINT, handler)


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    arg_parser = argparse.ArgumentParser(description="UCF Catalog Professor Scraper")
    arg_parser.add_argument(
        "--scrape",
        action="store_true",
        help="Fetch and parse the UCF catalog and save results to JSON.",
    )
    return arg_parser.parse_args()


def main() -> None:
    """Entry point: parse args and run the scrape."""
    args = _parse_args()

    if not args.scrape:
        print("Please specify an action. Use --scrape.")
        return

    engine, monitor = _build_engine()
    _setup_signal_handler(monitor)

    try:
        engine.run()
    except Exception as exc:
        print(f"\n[!] An error occurred: {exc}")
        monitor.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
