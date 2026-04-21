import threading
from typing import Optional, Any

from tqdm import tqdm


class Monitor:
    """Manages tqdm progress bars for the professor and review scraping phases.

    All operations are thread-safe via an internal lock so concurrent threads
    can safely update progress without corrupting the bars.
    """

    def __init__(self) -> None:
        """Initialises the monitor with no active progress bars."""
        self._prof_pbar: Optional[Any] = None
        self._review_pbar: Optional[Any] = None
        self._lock = threading.Lock()

    def init_professors(self, total: int) -> None:
        """Creates the professor progress bar with the given total count.

        Args:
            total: The expected number of professors to fetch.
        """
        with self._lock:
            self._prof_pbar = tqdm(total=total, desc="Professors fetched", position=0)

    def update_professors(self, n: int = 1) -> None:
        """Advances the professor progress bar by n steps.

        Args:
            n: Number of steps to advance.
        """
        with self._lock:
            if self._prof_pbar is not None:
                self._prof_pbar.update(n)

    def init_reviews(self, total: int) -> None:
        """Creates the review progress bar with the given total count.

        Args:
            total: The expected number of professors whose reviews will be fetched.
        """
        with self._lock:
            self._review_pbar = tqdm(total=total, desc="Professors whose reviews are all fetched", position=1)

    def update_reviews(self, n: int = 1) -> None:
        """Advances the review progress bar by n steps.

        Args:
            n: Number of steps to advance.
        """
        with self._lock:
            if self._review_pbar is not None:
                self._review_pbar.update(n)

    def close(self) -> None:
        """Closes both progress bars, suppressing any errors from already-closed bars."""
        with self._lock:
            self._close_bar(self._prof_pbar)
            self._close_bar(self._review_pbar)

    def _close_bar(self, bar: Optional[Any]) -> None:
        """Safely closes a single tqdm bar, ignoring any exception.

        Args:
            bar: The tqdm bar instance to close, or None.
        """
        if bar is not None:
            try:
                bar.close()
            except Exception:
                pass
