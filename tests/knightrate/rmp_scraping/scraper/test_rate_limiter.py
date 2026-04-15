import time
import threading
from knightrate.rmp_scraping.scraper.rate_limiter import RateLimiter

def test_rate_limiter_throttling():
    limiter = RateLimiter(rate=20.0)
    limiter.allowance = 0.0
    
    start_time = time.time()
    for _ in range(5):
        limiter.wait()
    duration = time.time() - start_time
    
    # 5 requests at 20 res/sec means around 5 * 0.05 = 0.25 sec
    assert duration >= 0.15 # Minimum threshold

def worker(limiter, results, index):
    limiter.wait()
    results[index] = time.time()

def test_rate_limiter_multithreaded():
    limiter = RateLimiter(rate=10.0)
    limiter.allowance = 0.0
    threads = []
    results = [0] * 5
    
    start_time = time.time()
    for i in range(5):
        t = threading.Thread(target=worker, args=(limiter, results, i))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    duration = time.time() - start_time
    assert duration >= 0.35 # Should take at least 0.4s for 5 tokens at 10 tokens/sec
