import threading
from typing import Optional, Any

from tqdm import tqdm


class Monitor:
    """Manages a single tqdm progress bar for the catalog scrape."""

    def __init__(self):
        self._pbar: Optional[Any] = None
        self._lock = threading.Lock()

    def init(self, total: int) -> None:
        """Initialise the progress bar with a known total."""
        with self._lock:
            self._pbar = tqdm(total=total, desc="Professor entries scraped", unit="entry")

    def update(self, n: int = 1) -> None:
        """Advance the progress bar by *n* steps."""
        with self._lock:
            if self._pbar is not None:
                self._pbar.update(n)

    def close(self) -> None:
        """Safely close the progress bar."""
        with self._lock:
            try:
                if self._pbar is not None:
                    self._pbar.close()
            except Exception:
                pass
