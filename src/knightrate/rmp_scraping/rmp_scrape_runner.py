import os
import signal
import sys
from typing import Optional

from dotenv import load_dotenv
from .scraper.client import GraphQLClient
from .scraper.rate_limiter import RateLimiter
from .scraper.storage import DataStorage
from .scraper.monitor import Monitor
from .scraper.engine import ScraperEngine

_RMP_RATE = 5.0


class RmpScrapeRunner:
    """Orchestrates the RateMyProfessors scraping pipeline."""

    def __init__(
        self,
        output_dir: str,
        limit_professors: Optional[int] = None,
        limit_reviews: Optional[int] = None,
    ):
        self._output_dir = output_dir
        self._limit_professors = limit_professors
        self._limit_reviews = limit_reviews

    def run(self) -> None:
        """Runs the full RMP scraping pipeline (professor + reviews)."""
        load_dotenv()
        engine = self._build_engine()
        self._setup_signal_handler(engine)
        try:
            engine.run()
        except Exception as exc:
            print(f"\n[!] An error occurred during scraping: {exc}")
            engine.monitor.close()
            os._exit(1)

    def _build_engine(self) -> ScraperEngine:
        """Wires up all scraper components."""
        rate_limiter = RateLimiter(rate=_RMP_RATE)
        client = GraphQLClient(rate_limiter)
        storage = DataStorage(output_dir=self._output_dir)
        monitor = Monitor()
        return ScraperEngine(
            client,
            storage,
            monitor,
            limit_professors=self._limit_professors,
            limit_reviews=self._limit_reviews,
        )

    def _setup_signal_handler(self, engine: ScraperEngine) -> None:
        """Registers SIGINT handler for graceful shutdown."""
        def handler(sig, frame):
            print("\n[!] Scraping interrupted by user.")
            engine._is_cancelled = True
            for f in getattr(engine, "futures", []):
                f.cancel()
            engine.monitor.close()
            os._exit(1)
        signal.signal(signal.SIGINT, handler)
