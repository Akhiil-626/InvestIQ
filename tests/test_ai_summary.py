import pytest
from unittest.mock import patch, MagicMock
from data.ai_summary import get_educational_summary, _build_fallback_summary


class TestAISummary:
    """Tests for ai_summary.py using mocked requests."""

    def test_build_fallback_aligned(self):
        """Test fallback summary for aligned case."""
        summary = _build_fallback_summary('AAPL', 0.1, 0.2, -0.1, 'aligned')
        assert 'AAPL' in summary
        assert 'in line' in summary
        assert '0.10' in summary or '+0.10' in summary
        assert '0.20' in summary or '+0.20' in summary

    def test_build_fallback_retail_hotter(self):
        """Test fallback summary for retail hotter than price."""
        summary = _build_fallback_summary('TSLA', 0.8, 0.1, 0.7, 'retail hotter than price')
        assert 'TSLA' in summary
        assert 'hotter' in summary
        assert '0.80' in summary or '+0.80' in summary
        assert '0.10' in summary or '+0.10' in summary

    def test_build_fallback_price_ahead(self):
        """Test fallback summary for price moving ahead of chatter."""
        summary = _build_fallback_summary('NVDA', -0.2, 0.4, -0.6, 'price moving ahead of chatter')
        assert 'NVDA' in summary
        assert 'moving more' in summary
        assert '-0.20' in summary
        assert '0.40' in summary or '+0.40' in summary

    @patch('data.ai_summary.os.environ.get')
    def test_get_educational_summary_no_api_key(self, mock_env_get):
        """Test fallback used when no API key."""
        mock_env_get.return_value = None
        
        summary = get_educational_summary('AAPL', 0.5, -0.3, 0.8, 'retail hotter than price')
        assert 'AAPL' in summary
        assert 'hotter' in summary

    @patch('data.ai_summary.os.environ.get')
    @patch('data.ai_summary.requests.post')
    def test_get_educational_summary_success(self, mock_post, mock_env_get):
        """Test successful Grok API call."""
        mock_env_get.return_value = 'test-api-key'
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Grok says: sentiment is bullish but price is down."}}]
        }
        mock_post.return_value = mock_response
        
        summary = get_educational_summary('AAPL', 0.7, -0.2, 0.9, 'retail hotter than price')
        assert summary == "Grok says: sentiment is bullish but price is down."
        mock_post.assert_called_once()

    @patch('data.ai_summary.os.environ.get')
    @patch('data.ai_summary.requests.post')
    def test_get_educational_summary_api_error(self, mock_post, mock_env_get):
        """Test fallback when Grok API call fails."""
        mock_env_get.return_value = 'test-api-key'
        mock_post.side_effect = Exception("Network error")
        
        summary = get_educational_summary('AAPL', 0.7, -0.2, 0.9, 'retail hotter than price')
        # Should fall back to template summary
        assert 'AAPL' in summary
        assert 'hotter' in summary

    @patch('data.ai_summary.os.environ.get')
    @patch('data.ai_summary.requests.post')
    def test_get_educational_summary_http_error(self, mock_post, mock_env_get):
        """Test fallback when Grok returns HTTP error."""
        mock_env_get.return_value = 'test-api-key'
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_post.return_value = mock_response
        
        summary = get_educational_summary('AAPL', 0.7, -0.2, 0.9, 'retail hotter than price')
        assert 'AAPL' in summary
        assert 'hotter' in summary

    @patch('data.ai_summary.os.environ.get')
    @patch('data.ai_summary.requests.post')
    def test_get_educational_summary_malformed_response(self, mock_post, mock_env_get):
        """Test fallback when Grok returns unexpected response format."""
        mock_env_get.return_value = 'test-api-key'
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"choices": []}  # Missing expected structure
        mock_post.return_value = mock_response
        
        summary = get_educational_summary('AAPL', 0.7, -0.2, 0.9, 'retail hotter than price')
        assert 'AAPL' in summary
        assert 'hotter' in summary

    @patch('data.ai_summary.os.environ.get')
    @patch('data.ai_summary.requests.post')
    def test_get_educational_summary_request_params(self, mock_post, mock_env_get):
        """Test that request is made with correct parameters."""
        mock_env_get.return_value = 'test-api-key'
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test summary"}}]
        }
        mock_post.return_value = mock_response
        
        get_educational_summary('TEST', 0.5, 0.1, 0.4, 'aligned')
        
        call_args = mock_post.call_args
        assert call_args is not None
        assert call_args[0][0] == "https://api.x.ai/v1/chat/completions"
        assert call_args[1]['headers']['Authorization'] == "Bearer test-api-key"
        assert call_args[1]['json']['model'] == "grok-4.3"
        assert call_args[1]['json']['temperature'] == 0.4
        assert call_args[1]['json']['max_tokens'] == 150
        assert "TEST" in call_args[1]['json']['messages'][1]['content']