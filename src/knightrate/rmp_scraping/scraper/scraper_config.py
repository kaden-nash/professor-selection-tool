from dataclasses import dataclass
from typing import Optional

from .client import GraphQLClient
from .monitor import Monitor
from .storage import DataStorage


@dataclass
class ScraperConfig:
    """Bundles all dependencies and settings for ScraperEngine.

    Passing a single ScraperConfig into ScraperEngine keeps the constructor
    signature to one explicit argument while keeping all parts easily
    swappable for testing.

    Attributes:
        client: The GraphQL client used to query RateMyProfessors.
        storage: The data-storage layer for persisting scraped results.
        monitor: The progress-bar monitor for the scraping phases.
        limit_professors: Maximum number of professors to scrape, or None for all.
        limit_reviews: Maximum reviews per professor to scrape, or None for all.
    """

    client: GraphQLClient
    storage: DataStorage
    monitor: Monitor
    limit_professors: Optional[int] = None
    limit_reviews: Optional[int] = None
