from .scraper.client import CatalogClient
from .scraper.parser import CatalogParser
from .scraper.storage import DataStorage
from .scraper.engine import ScraperEngine, ScraperDependencies


class ProfScrapeRunner:
    """Orchestrates the UCF professor catalog scraping pipeline."""

    def __init__(self, output_dir: str):
        self._output_dir = output_dir

    def run(self) -> None:
        """Runs the full professor catalog scraping pipeline."""
        engine = self._build_engine()
        try:
            engine.run()
        except Exception as exc:
            print(f"\n[!] An error occurred: {exc}")
            raise exc

    def _build_engine(self) -> ScraperEngine:
        """Wires up all scraper components."""
        client = CatalogClient()
        parser = CatalogParser()
        storage = DataStorage(self._output_dir)
        deps = ScraperDependencies(
            client=client,
            parser=parser,
            storage=storage,
        )
        return ScraperEngine(deps)
