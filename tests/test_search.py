from app.tools.search import tavily_search
from unittest.mock import patch

def test_tavily_search_graceful_degradation():
    # Mock the client to always raise an exception
    with patch("app.tools.search._client.search", side_effect=Exception("API Timeout")) as mock_search:
        # We can also mock time.sleep to avoid actually waiting during the test
        with patch("app.tools.search.time.sleep") as mock_sleep:
            import pytest
            from app.tools.search import SearchUnavailableError
            with pytest.raises(SearchUnavailableError, match="API Timeout"):
                tavily_search("Acme Corp")
            
            # Should have retried 3 times
            assert mock_search.call_count == 3
