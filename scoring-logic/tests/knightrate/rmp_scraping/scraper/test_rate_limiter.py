import time
import threading

import pytest

from src.knightrate.rmp_scraping.scraper.rate_limiter import RateLimiter


class TestRateLimiter:
    """Unit tests for RateLimiter."""

    def test_allows_immediate_request_when_full(self):
        """A freshly initialised limiter should not block the first request."""
        limiter = RateLimiter(rate=1.0)
        start = time.time()
        limiter.wait()
        assert time.time() - start < 0.1

    def test_throttles_sequential_requests(self):
        """Sequential requests beyond initial allowance should be delayed."""
        limiter = RateLimiter(rate=20.0)
        limiter._allowance = 0.0

        start = time.time()
        for _ in range(5):
            limiter.wait()
        duration = time.time() - start

        assert duration >= 0.15

    def test_multithreaded_throttling(self):
        """Concurrent threads should each be rate-limited."""
        limiter = RateLimiter(rate=10.0)
        limiter._allowance = 0.0
        results = [0.0] * 5

        def worker(index):
            limiter.wait()
            results[index] = time.time()

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert time.time() - start >= 0.35

    def test_refills_allowance_over_time(self):
        """After waiting, the limiter should refill and allow a request quickly."""
        limiter = RateLimiter(rate=10.0)
        limiter._allowance = 0.0
        time.sleep(0.15)
        start = time.time()
        limiter.wait()
        assert time.time() - start < 0.1
