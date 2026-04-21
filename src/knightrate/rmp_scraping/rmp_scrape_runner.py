import os
import signal
from dataclasses import dataclass

from dotenv import load_dotenv
from pathlib import Path

from .scraper.client import GraphQLClient
from .scraper.engine import ScraperEngine
from .scraper.monitor import Monitor
from .scraper.rate_limiter import RateLimiter
from .scraper.scraper_config import ScraperConfig
from .scraper.storage import DataStorage

_RMP_RATE = 5.0

@dataclass
class ScraperArgs:
    """All configuration flags for the RMP scraper passed to the main pipeline orchestrator."""
    reviews_only: bool = False
    limit_profs: int | None = None
    limit_reviews_per_prof: int | None = None

class RmpScrapeRunner:
    """Orchestrates the RateMyProfessors scraping pipeline.

    Builds all internal components, wires them together through a
    ScraperConfig, and delegates execution to ScraperEngine.
    """

    def __init__(
        self,
        output_dir: Path,
        scraper_args: ScraperArgs
    ) -> None:
        """Initialises the runner with output configuration and optional limits.

        Args:
            output_dir: Directory where all scraped output files are written.
            scraper_args: Dataclass containing all configuration information for running the scraper.
        """
        self._output_dir = output_dir
        self._limit_professors = scraper_args.limit_profs
        self._limit_reviews = scraper_args.limit_reviews_per_prof
        self._reviews_only = scraper_args.reviews_only

    def run(self) -> None:
        """Runs the full RMP scraping pipeline (professors + reviews).

        Raises:
            Exception: Re-raises any exception thrown during scraping after
                       cancelling in-flight work and freeing monitor resources.
        """
        load_dotenv()
        engine = self._build_engine()
        self._setup_signal_handler(engine)
        try:
            print("Beginning RMP scraping...")
            self.choose_run_based_on_args(engine)
            print("Completed RMP scraping.")
        except Exception as exc:
            print(f"\n[!] An error occurred during scraping: {exc}")
            engine.cancel()
            raise

    def choose_run_based_on_args(self, engine: ScraperEngine) -> None:
        """Delegates to the appropriate engine run mode based on the reviews_only flag.

        Args:
            engine: The configured ScraperEngine to delegate to.
        """
        if self._reviews_only:
            engine.run_reviews_only()
        else:
            engine.run()

    def _build_engine(self) -> ScraperEngine:
        """Constructs and wires all scraper components into a ScraperEngine.

        Returns:
            A fully configured ScraperEngine ready to run.
        """
        rate_limiter = RateLimiter(rate=_RMP_RATE)
        config = ScraperConfig(
            client=GraphQLClient(rate_limiter),
            storage=DataStorage(output_dir=self._output_dir),
            monitor=Monitor(),
            limit_professors=self._limit_professors,
            limit_reviews=self._limit_reviews,
        )
        return ScraperEngine(config)

    def _setup_signal_handler(self, engine: ScraperEngine) -> None:
        """Registers a SIGINT handler for graceful shutdown.

        Args:
            engine: The running ScraperEngine to cancel on interrupt.
        """
        def handler(sig, frame):
            print("\n[!] Scraping interrupted by user.")
            engine.cancel()
            os._exit(1)

        signal.signal(signal.SIGINT, handler)
