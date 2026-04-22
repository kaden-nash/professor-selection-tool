import os

import pytest
import requests_mock as req_mock_lib

from src.knightrate.rmp_scraping.scraper.client import (
    GraphQLClient,
    GraphQLRequest,
    GraphQLRequestError,
)
from src.knightrate.rmp_scraping.scraper.rate_limiter import RateLimiter

_ENDPOINT = "https://www.ratemyprofessors.com/graphql"


def _make_request(operation_name: str = "TestQuery", max_retries: int = 1) -> GraphQLRequest:
    return GraphQLRequest(
        query="query {}",
        variables={},
        operation_name=operation_name,
        max_retries=max_retries,
    )


def _fast_limiter() -> RateLimiter:
    return RateLimiter(rate=200.0)


class TestGraphQLClient:
    """Unit tests for GraphQLClient."""

    def test_successful_request(self):
        client = GraphQLClient(_fast_limiter())
        with req_mock_lib.Mocker() as m:
            m.post(_ENDPOINT, json={"data": "success"}, status_code=200)
            result = client.execute(_make_request())
        assert result == {"data": "success"}

    def test_retries_and_raises_on_repeated_failure(self):
        client = GraphQLClient(_fast_limiter())
        with req_mock_lib.Mocker() as m:
            m.post(_ENDPOINT, status_code=500)
            with pytest.raises(GraphQLRequestError, match="Failed to execute"):
                client.execute(_make_request(max_retries=2))
            assert m.call_count == 2

    def test_raises_on_graphql_errors_in_200_response(self):
        client = GraphQLClient(_fast_limiter())
        with req_mock_lib.Mocker() as m:
            m.post(_ENDPOINT, json={"errors": [{"message": "Not found"}]}, status_code=200)
            with pytest.raises(GraphQLRequestError):
                client.execute(_make_request(max_retries=1))

    def test_raises_on_json_decode_failure(self):
        client = GraphQLClient(_fast_limiter())
        with req_mock_lib.Mocker() as m:
            m.post(_ENDPOINT, text="not-json", status_code=200)
            with pytest.raises(GraphQLRequestError):
                client.execute(_make_request(max_retries=1))

    def test_handles_requests_exception(self):
        import requests

        client = GraphQLClient(_fast_limiter())
        with req_mock_lib.Mocker() as m:
            m.post(_ENDPOINT, exc=requests.ConnectionError("refused"))
            with pytest.raises(GraphQLRequestError) as exc_info:
                client.execute(_make_request(max_retries=1))
        assert "Requests module exception" in exc_info.value.last_error

    def test_proxy_configured_from_env(self, monkeypatch):
        monkeypatch.setenv("PROXYRACK_URL", "proxy.example.com:8080")
        monkeypatch.setenv("PROXYRACK_USERNAME", "user")
        monkeypatch.setenv("PROXYRACK_PASSWORD", "pass")
        client = GraphQLClient(_fast_limiter())
        assert "proxy.example.com" in client._session.proxies.get("http", "")

    def test_proxy_not_set_when_env_missing(self, monkeypatch):
        monkeypatch.delenv("PROXYRACK_URL", raising=False)
        client = GraphQLClient(_fast_limiter())
        assert not client._session.proxies

    def test_proxy_no_auth_when_credentials_missing(self, monkeypatch):
        monkeypatch.setenv("PROXYRACK_URL", "proxy.example.com:8080")
        monkeypatch.delenv("PROXYRACK_USERNAME", raising=False)
        monkeypatch.delenv("PROXYRACK_PASSWORD", raising=False)
        client = GraphQLClient(_fast_limiter())
        proxy = client._session.proxies.get("http", "")
        assert "@" not in proxy
        assert "proxy.example.com" in proxy
