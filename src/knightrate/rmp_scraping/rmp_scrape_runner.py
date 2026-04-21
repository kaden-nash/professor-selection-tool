import os
import signal

from dotenv import load_dotenv

from .scraper.client import GraphQLClient
from .scraper.engine import ScraperEngine
from .scraper.monitor import Monitor
from .scraper.rate_limiter import RateLimiter
from .scraper.scraper_config import ScraperConfig
from .scraper.storage import DataStorage

_RMP_RATE = 5.0


class RmpScrapeRunner:
    """Orchestrates the RateMyProfessors scraping pipeline.

    Builds all internal components, wires them together through a
    ScraperConfig, and delegates execution to ScraperEngine.
    """

    def __init__(
        self,
        output_dir: str,
        limit_professors: "int | None" = None,
        limit_reviews: "int | None" = None,
    ) -> None:
        """Initialises the runner with output configuration and optional limits.

        Args:
            output_dir: Directory where all scraped output files are written.
            limit_professors: Maximum number of professors to scrape. None for all.
            limit_reviews: Maximum reviews per professor to scrape. None for all.
        """
        self._output_dir = output_dir
        self._limit_professors = limit_professors
        self._limit_reviews = limit_reviews

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
            engine.run()
            print("Completed RMP scraping.")
        except Exception as exc:
            print(f"\n[!] An error occurred during scraping: {exc}")
            engine.cancel()
            raise

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
