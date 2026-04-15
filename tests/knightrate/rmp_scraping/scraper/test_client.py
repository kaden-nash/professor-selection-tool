import pytest
import requests_mock
from knightrate.rmp_scraping.scraper.client import GraphQLClient
from knightrate.rmp_scraping.scraper.rate_limiter import RateLimiter

def test_client_success():
    limiter = RateLimiter(rate=100.0)
    client = GraphQLClient(limiter)
    
    with requests_mock.Mocker() as m:
        m.post("https://www.ratemyprofessors.com/graphql", json={"data": "success"}, status_code=200)
        
        result = client.execute("query", {}, "TestQuery", max_retries=1)
        assert result == {"data": "success"}

def test_client_retry_and_fail():
    limiter = RateLimiter(rate=200.0)  # fast rate limit for test
    client = GraphQLClient(limiter)
    
    with requests_mock.Mocker() as m:
        m.post("https://www.ratemyprofessors.com/graphql", status_code=500)
        
        with pytest.raises(Exception, match="Failed to execute GraphQL query"):
            # Set max_retries to 2 to test the retry and exception logic quickly
            client.execute("query", {}, "TestQuery", max_retries=2)
            
        assert m.call_count == 2
