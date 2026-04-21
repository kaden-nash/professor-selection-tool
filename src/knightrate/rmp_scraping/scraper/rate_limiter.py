import time
import threading

_SLEEP_TICK_S = 0.05


class RateLimiter:
    """Thread-safe token-bucket rate limiter.

    Enforces a maximum number of requests per second across all threads
    by blocking callers until a token is available.
    """

    def __init__(self, rate: float) -> None:
        """Initialises the limiter with the given requests-per-second rate.

        Args:
            rate: Maximum number of requests allowed per second.
        """
        self._rate = rate
        self._allowance = rate
        self._last_check = time.time()
        self._lock = threading.Lock()

    def wait(self) -> None:
        """Blocks the calling thread until a token is available for a request."""
        while True:
            with self._lock:
                if self._try_consume_token():
                    return
            time.sleep(_SLEEP_TICK_S)

    def _try_consume_token(self) -> bool:
        """Refills the bucket and consumes one token if available.

        Returns:
            True if a token was consumed; False if the bucket is empty.
        """
        current = time.time()
        time_passed = current - self._last_check
        self._last_check = current

        self._allowance += time_passed * self._rate
        if self._allowance > self._rate:
            self._allowance = self._rate

        if self._allowance >= 1.0:
            self._allowance -= 1.0
            return True
        return False
