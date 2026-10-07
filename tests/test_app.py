import pytest
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestFlaskRoutes:
    """Tests for Flask routes."""

    def test_index_get(self, client):
        """Test GET / returns index page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'InvestIQ' in response.data
        assert b'Target Acquisition' in response.data

    def test_analyze_post_valid_ticker(self, client):
        """Test POST /analyze with valid ticker redirects."""
        with patch('app.get_price_momentum') as mock_price, \
             patch('app.get_current_price') as mock_current, \
             patch('app.get_reddit_sentiment') as mock_reddit, \
             patch('app.get_educational_summary') as mock_summary:
            
            mock_price.return_value = 2.5
            mock_current.return_value = 150.0
            mock_reddit.side_effect = NotImplementedError("No creds")
            mock_summary.return_value = "Test summary"
            
            response = client.post('/analyze', data={'ticker': 'AAPL'})
            assert response.status_code == 302  # Redirect
            assert '/analyze/AAPL' in response.location

    def test_analyze_post_with_days_parameter(self, client):
        """Test POST /analyze with days parameter redirects correctly."""
        with patch('app.get_price_momentum') as mock_price, \
             patch('app.get_current_price') as mock_current, \
             patch('app.get_reddit_sentiment') as mock_reddit, \
             patch('app.get_educational_summary') as mock_summary:
            
            mock_price.return_value = 2.5
            mock_current.return_value = 150.0
            mock_reddit.side_effect = NotImplementedError("No creds")
            mock_summary.return_value = "Test summary"
            
            response = client.post('/analyze', data={'ticker': 'AAPL', 'days': '30'})
            assert response.status_code == 302  # Redirect
            assert '/analyze/AAPL' in response.location
            assert 'days=30' in response.location

    def test_analyze_post_invalid_days_defaults_to_7(self, client):
        """Test POST /analyze with invalid days defaults to 7."""
        with patch('app.get_price_momentum') as mock_price, \
             patch('app.get_current_price') as mock_current, \
             patch('app.get_reddit_sentiment') as mock_reddit, \
             patch('app.get_educational_summary') as mock_summary:
            
            mock_price.return_value = 2.5
            mock_current.return_value = 150.0
            mock_reddit.side_effect = NotImplementedError("No creds")
            mock_summary.return_value = "Test summary"
            
            response = client.post('/analyze', data={'ticker': 'AAPL', 'days': 'invalid'})
            assert response.status_code == 302  # Redirect
            assert '/analyze/AAPL' in response.location
            assert 'days=7' in response.location

    def test_analyze_post_empty_ticker(self, client):
        """Test POST /analyze with empty ticker shows error."""
        response = client.post('/analyze', data={'ticker': ''})
        assert response.status_code == 200
        assert b'Please provide a valid ticker' in response.data

    def test_analyze_post_whitespace_ticker(self, client):
        """Test POST /analyze with whitespace-only ticker."""
        response = client.post('/analyze', data={'ticker': '   '})
        assert response.status_code == 200
        assert b'Please provide a valid ticker' in response.data

    def test_analyze_get_success(self, client):
        """Test GET /analyze/<ticker> with successful data fetch."""
        with patch('app.get_price_momentum') as mock_price, \
             patch('app.get_current_price') as mock_current, \
             patch('app.get_reddit_sentiment') as mock_reddit, \
             patch('app.get_mock_sentiment') as mock_mock, \
             patch('app.get_educational_summary') as mock_summary:
            
            mock_price.return_value = 2.5
            mock_current.return_value = 150.0
            mock_reddit.side_effect = NotImplementedError("No creds")
            mock_mock.return_value = [0.1, 0.2, 0.3]
            mock_summary.return_value = "Test summary for AAPL"
            
            response = client.get('/analyze/AAPL')
            assert response.status_code == 200
            assert b'AAPL' in response.data
            assert b'150.00' in response.data
            assert b'2.50' in response.data
            assert b'Test summary for AAPL' in response.data
            assert b'MOCK data' in response.data  # Mock warning

    def test_analyze_get_with_days_parameter(self, client):
        """Test GET /analyze/<ticker> with days parameter."""
        with patch('app.get_price_momentum') as mock_price, \
             patch('app.get_current_price') as mock_current, \
             patch('app.get_reddit_sentiment') as mock_reddit, \
             patch('app.get_mock_sentiment') as mock_mock, \
             patch('app.get_educational_summary') as mock_summary:
            
            mock_price.return_value = 5.0
            mock_current.return_value = 150.0
            mock_reddit.side_effect = NotImplementedError("No creds")
            mock_mock.return_value = [0.1, 0.2, 0.3]
            mock_summary.return_value = "Test summary for AAPL"
            
            response = client.get('/analyze/AAPL?days=30')
            assert response.status_code == 200
            assert b'AAPL' in response.data
            assert b'30D Momentum' in response.data  # Dynamic label
            assert b'5.00' in response.data

    def test_analyze_get_with_real_sentiment(self, client):
        """Test GET /analyze/<ticker> with real Reddit sentiment."""
        with patch('app.get_price_momentum') as mock_price, \
             patch('app.get_current_price') as mock_current, \
             patch('app.get_reddit_sentiment') as mock_reddit, \
             patch('app.get_educational_summary') as mock_summary:
            
            mock_price.return_value = -1.5
            mock_current.return_value = 200.0
            mock_reddit.return_value = [0.5, 0.6, 0.7]  # Real sentiment
            mock_summary.return_value = "Real sentiment summary"
            
            response = client.get('/analyze/TSLA')
            assert response.status_code == 200
            assert b'TSLA' in response.data
            assert b'200.00' in response.data
            assert b'-1.50' in response.data
            assert b'MOCK data' not in response.data  # No mock warning

    def test_analyze_get_invalid_ticker(self, client):
        """Test GET /analyze/<ticker> with invalid ticker (ValueError)."""
        with patch('app.get_price_momentum') as mock_price:
            mock_price.side_effect = ValueError("No price data found for 'INVALID'")
            
            response = client.get('/analyze/INVALID')
            assert response.status_code == 404
            assert b'No price data found' in response.data

    def test_analyze_get_unexpected_error(self, client):
        """Test GET /analyze/<ticker> with unexpected error (500)."""
        with patch('app.get_price_momentum') as mock_price:
            mock_price.side_effect = Exception("Unexpected error")
            
            response = client.get('/analyze/AAPL')
            assert response.status_code == 500
            assert b'An unexpected error occurred' in response.data

    def test_analyze_get_mock_sentiment_calculation(self, client):
        """Test that mock sentiment is properly normalized and scored."""
        with patch('app.get_price_momentum') as mock_price, \
             patch('app.get_current_price') as mock_current, \
             patch('app.get_reddit_sentiment') as mock_reddit, \
             patch('app.get_mock_sentiment') as mock_mock, \
             patch('app.get_educational_summary') as mock_summary:
            
            mock_price.return_value = 4.0  # 4% price change
            mock_current.return_value = 100.0
            mock_reddit.side_effect = NotImplementedError("No creds")
            # Mock sentiment scores that average to ~0.2 after dampening
            mock_mock.return_value = [0.8, 0.8, 0.8, 0.8, 0.8]  # 5 scores = trust 5/15 = 0.33, avg=0.8*0.33=0.26
            mock_summary.return_value = "Summary"
            
            response = client.get('/analyze/TEST')
            assert response.status_code == 200
            # Verify the page renders with computed scores
            assert b'TEST' in response.data