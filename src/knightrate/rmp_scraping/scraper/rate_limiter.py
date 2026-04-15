import time
import threading

class RateLimiter:
    def __init__(self, rate: float):
        """
        Thread-safe token bucket rate limiter.
        :param rate: Maximum number of requests per second.
        """
        self.rate = rate
        self.allowance = rate
        self.last_check = time.time()
        self.lock = threading.Lock()
        
    def wait(self):
        """
        Blocks the current thread until a token (allowance) is available for a request.
        """
        while True:
            with self.lock:
                current = time.time()
                time_passed = current - self.last_check
                self.last_check = current
                
                self.allowance += time_passed * self.rate
                if self.allowance > self.rate:
                    self.allowance = self.rate
                
                if self.allowance >= 1.0:
                    self.allowance -= 1.0
                    return
            # Sleep outside the lock so we don't block other threads
            time.sleep(0.05)
