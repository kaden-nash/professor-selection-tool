import os
import time
import random
import requests  
from typing import Dict, Any
from .rate_limiter import RateLimiter  

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

class GraphQLRequestError(Exception):
    def __init__(self, message: str, payload: Dict[str, Any], last_error: str = ""):
        super().__init__(message)
        self.payload = payload
        self.last_error = last_error

class GraphQLClient:
    def __init__(self, rate_limiter: RateLimiter):
        """
        Initializes the GraphQL client with proxy setup and a shared rate limiter.
        """
        self.endpoint = "https://www.ratemyprofessors.com/graphql"
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
        
        # Setup proxyrack if configured
        proxy_url = os.getenv("PROXYRACK_URL")
        proxy_user = os.getenv("PROXYRACK_USERNAME")
        proxy_pass = os.getenv("PROXYRACK_PASSWORD")
        if proxy_url:
            auth = f"{proxy_user}:{proxy_pass}@" if proxy_user and proxy_pass else ""
            proxy_str = f"http://{auth}{proxy_url}"
            self.session.proxies = {
                "http": proxy_str,
                "https": proxy_str
            }
            
    def _get_random_headers(self) -> Dict[str, str]:
        """
        Returns a dictionary of headers with a rotated User-Agent to avoid detection.
        """
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://www.ratemyprofessors.com",
            "Referer": "https://www.ratemyprofessors.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        
    def execute(self, query: str, variables: Dict[str, Any], operation_name: str, max_retries: int = 5) -> Dict[str, Any]:
        """
        Executes a GraphQL query with jittered exponential backoff and rate limiting.
        """
        payload = {
            "query": query,
            "variables": variables,
            "operationName": operation_name
        }
        
        base_delay = 2.0
        last_error = "Unknown error occurred before requests were made."
        
        for attempt in range(max_retries):
            self.rate_limiter.wait()
            headers = self._get_random_headers()
            
            try:
                response = self.session.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if "errors" in data and len(data.get("errors", [])) > 0:
                            last_error = f"HTTP 200 but GraphQL returned errors: {data['errors']}"
                        else:
                            return data
                    except ValueError:
                        last_error = f"JSON decode failed. Response text: {response.text[:200]}"
                else:
                    last_error = f"HTTP {response.status_code}. Response text: {response.text[:200]}"
                
            except requests.RequestException as e:
                last_error = f"Requests module exception: {str(e)}"
                
            # If we reached here, the request failed. Apply jittered exponential backoff.
            if attempt < max_retries - 1:
                # e.g., attempt 0: 2s + jitter, attempt 1: 4s + jitter, attempt 2: 8s + jitter
                sleep_time = base_delay * (2 ** attempt) + random.uniform(0.1, 1.5)
                time.sleep(sleep_time)
                
                
        raise GraphQLRequestError(f"Failed to execute GraphQL query '{operation_name}' after {max_retries} attempts. Last Error: {last_error}", payload, last_error)
