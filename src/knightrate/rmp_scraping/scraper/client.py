import os
import time
import random
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple

import requests

from .rate_limiter import RateLimiter

_DEFAULT_MAX_RETRIES = 5
_BASE_DELAY_S = 2.0
_MIN_JITTER_S = 0.1
_MAX_JITTER_S = 1.5
_REQUEST_TIMEOUT_S = 15
_INITIAL_ERROR_MSG = "Unknown error occurred before any request was made."

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

_RMP_ENDPOINT = "https://www.ratemyprofessors.com/graphql"


@dataclass
class GraphQLRequest:
    """Bundles all data needed to dispatch one GraphQL request.

    Attributes:
        query: The GraphQL query string.
        variables: A dict of query variables.
        operation_name: The named operation inside the query.
        max_retries: Maximum number of attempts before raising.
    """

    query: str
    variables: Dict[str, Any]
    operation_name: str
    max_retries: int = field(default=_DEFAULT_MAX_RETRIES)


class GraphQLRequestError(Exception):
    """Raised when a GraphQL request fails after all retries.

    Attributes:
        payload: The request payload that failed.
        last_error: A human-readable description of the most recent error.
    """

    def __init__(self, message: str, payload: Dict[str, Any], last_error: str = "") -> None:
        super().__init__(message)
        self.payload = payload
        self.last_error = last_error


class GraphQLClient:
    """HTTP client for the RateMyProfessors GraphQL endpoint.

    Applies rate limiting, random User-Agent rotation, optional proxy
    configuration, and jittered exponential back-off on failures.
    """

    def __init__(self, rate_limiter: RateLimiter) -> None:
        """Initialises the client with a shared rate limiter and optional proxy.

        Args:
            rate_limiter: A RateLimiter instance that gates outbound requests.
        """
        self._rate_limiter = rate_limiter
        self._session = requests.Session()
        self._endpoint = _RMP_ENDPOINT
        self._configure_proxy()

    def execute(self, request: GraphQLRequest) -> Dict[str, Any]:
        """Executes a GraphQL request with retries and exponential back-off.

        Args:
            request: The GraphQLRequest describing the query to run.

        Returns:
            The parsed JSON data from a successful response.

        Raises:
            GraphQLRequestError: If all retry attempts fail.
        """
        payload = {
            "query": request.query,
            "variables": request.variables,
            "operationName": request.operation_name,
        }
        return self._execute_with_retries(payload, request.max_retries)

    def _configure_proxy(self) -> None:
        """Reads proxy settings from environment variables and applies them to the session."""
        proxy_url = os.getenv("PROXYRACK_URL")
        if not proxy_url:
            return
        proxy_str = self._build_proxy_string(proxy_url)
        self._session.proxies = {"http": proxy_str, "https": proxy_str}

    def _build_proxy_string(self, proxy_url: str) -> str:
        """Constructs a proxy URL string with optional basic-auth credentials.

        Args:
            proxy_url: The host:port of the proxy server.

        Returns:
            A fully-formed proxy URL string.
        """
        user = os.getenv("PROXYRACK_USERNAME")
        password = os.getenv("PROXYRACK_PASSWORD")
        auth = f"{user}:{password}@" if user and password else ""
        return f"http://{auth}{proxy_url}"

    def _execute_with_retries(self, payload: Dict, max_retries: int) -> Dict[str, Any]:
        """Retries the request up to max_retries times with exponential back-off.

        Args:
            payload: The raw request payload dict.
            max_retries: Maximum number of attempts.

        Returns:
            Parsed JSON data on success.

        Raises:
            GraphQLRequestError: After all attempts are exhausted.
        """
        last_error = _INITIAL_ERROR_MSG
        for attempt in range(max_retries):
            data, last_error = self._attempt_single_request(payload)
            if data is not None:
                return data
            if attempt < max_retries - 1:
                self._sleep_with_backoff(attempt)
        raise GraphQLRequestError(
            f"Failed to execute '{payload['operationName']}' after {max_retries} attempts.",
            payload,
            last_error,
        )

    def _attempt_single_request(self, payload: Dict) -> Tuple[Optional[Dict[str, Any]], str]:
        """Makes one HTTP POST attempt.

        Args:
            payload: The raw request payload dict.

        Returns:
            A (data, error_msg) tuple. data is None when the attempt fails.
        """
        self._rate_limiter.wait()
        headers = self._get_random_headers()
        try:
            response = self._session.post(
                self._endpoint, json=payload, headers=headers, timeout=_REQUEST_TIMEOUT_S
            )
            return self._parse_response(response)
        except requests.RequestException as exc:
            return None, f"Requests module exception: {str(exc)}"

    def _parse_response(self, response: requests.Response) -> Tuple[Optional[Dict[str, Any]], str]:
        """Parses an HTTP response into (data, error_msg).

        Args:
            response: The HTTP response object.

        Returns:
            A (data, error_msg) tuple. data is None on any failure.
        """
        if response.status_code != 200:
            return None, f"HTTP {response.status_code}. Response text: {response.text[:200]}"
        try:
            data = response.json()
            if data.get("errors"):
                return None, f"GraphQL returned errors: {data['errors']}"
            return data, ""
        except ValueError:
            return None, f"JSON decode failed. Response text: {response.text[:200]}"

    def _sleep_with_backoff(self, attempt: int) -> None:
        """Sleeps for a jittered exponential duration based on the attempt number.

        Args:
            attempt: Zero-based attempt index used to compute the back-off delay.
        """
        delay = _BASE_DELAY_S * (2 ** attempt) + random.uniform(_MIN_JITTER_S, _MAX_JITTER_S)
        time.sleep(delay)

    def _get_random_headers(self) -> Dict[str, str]:
        """Returns request headers with a randomly chosen User-Agent.

        Returns:
            A headers dict suitable for sending to the RMP GraphQL endpoint.
        """
        return {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://www.ratemyprofessors.com",
            "Referer": "https://www.ratemyprofessors.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
