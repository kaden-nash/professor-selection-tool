import os
import argparse
import signal
from dotenv import load_dotenv
from scraper.client import GraphQLClient  
from scraper.rate_limiter import RateLimiter  
from scraper.storage import DataStorage  
from scraper.monitor import Monitor  
from scraper.engine import ScraperEngine  

def main():
    parser = argparse.ArgumentParser(description="RateMyProfessors Scraper")
    parser.add_argument("--all", action="store_true", help="Run a full standard scrape.")
    parser.add_argument("--reviews-only", action="store_true", help="Only fetch reviews for already known professors, skipping the professor search phase.")
    parser.add_argument("--retry-failed", action="store_true", help="Retry only specific failed requests stored in failed_requests.json.")
    parser.add_argument("--limit-professors", type=int, default=None, help="Limit the number of professors scraped (for testing).")
    parser.add_argument("--limit-reviews", type=int, default=None, help="Limit the number of reviews scraped per professor (for testing).")
    args = parser.parse_args()

    # Load configuration
    load_dotenv()
    
    # Spec requests global rate limit of 5 req/s across 200 threads
    rate_limiter = RateLimiter(rate=5.0)
    
    client = GraphQLClient(rate_limiter)
    
    # Store data relative to main.py
    storage = DataStorage()
    monitor = Monitor()
    
    engine = ScraperEngine(client, storage, monitor, limit_professors=args.limit_professors, limit_reviews=args.limit_reviews)
    
    def signal_handler(sig, frame):
        print("\n[!] Scraping interrupted by user.")
        if hasattr(engine, '_is_cancelled'):
            engine._is_cancelled = True
        
        if hasattr(engine, 'futures'):
            for f in getattr(engine, 'futures', []):
                f.cancel()
        
        monitor.close()
        os._exit(1)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        if args.retry_failed:
            engine.retry_failed_requests()
        elif args.reviews_only:
            engine.run_reviews_only()
        elif args.all:
            engine.run()
        else:
            print("Please specify an action. Use --all, --reviews-only, or --retry-failed.")
    except Exception as e:
        print(f"\n[!] An error occurred during scraping: {e}")
        monitor.close()
        os._exit(1)

if __name__ == "__main__":
    main()
