import pytest
from unittest.mock import patch, MagicMock
from data.reddit_sentiment import get_mock_sentiment, get_reddit_sentiment


class TestRedditSentiment:
    """Tests for reddit_sentiment.py using mocked PRAW and VADER."""

    def test_get_mock_sentiment_deterministic(self):
        """Test that mock sentiment is deterministic for same ticker."""
        scores1 = get_mock_sentiment('AAPL')
        scores2 = get_mock_sentiment('AAPL')
        assert scores1 == scores2
        assert len(scores1) == 15

    def test_get_mock_sentiment_different_tickers(self):
        """Test that different tickers produce different scores."""
        scores_aapl = get_mock_sentiment('AAPL')
        scores_tsla = get_mock_sentiment('TSLA')
        assert scores_aapl != scores_tsla

    def test_get_mock_sentiment_range(self):
        """Test that mock sentiment scores are in [-1, 1] range."""
        scores = get_mock_sentiment('AAPL')
        for score in scores:
            assert -1.0 <= score <= 1.0

    def test_get_mock_sentiment_custom_count(self):
        """Test custom num_posts parameter."""
        scores = get_mock_sentiment('AAPL', num_posts=10)
        assert len(scores) == 10

    @patch('data.reddit_sentiment.os.environ.get')
    def test_get_reddit_sentiment_missing_credentials(self, mock_env_get):
        """Test NotImplementedError when credentials missing."""
        mock_env_get.side_effect = lambda key, default='': default if key in ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET'] else ''
        
        with pytest.raises(NotImplementedError, match="Reddit credentials"):
            get_reddit_sentiment('AAPL')

    @patch('data.reddit_sentiment.os.environ.get')
    @patch('data.reddit_sentiment.praw.Reddit')
    def test_get_reddit_sentiment_success(self, mock_reddit_class, mock_env_get):
        """Test successful Reddit sentiment fetching."""
        mock_env_get.side_effect = lambda key, default='': 'test_id' if key == 'REDDIT_CLIENT_ID' else ('test_secret' if key == 'REDDIT_CLIENT_SECRET' else default)
        
        # Mock PRAW submission
        mock_submission = MagicMock()
        mock_submission.title = "AAPL to the moon!"
        mock_submission.selftext = "This stock is amazing"
        
        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = [mock_submission]
        
        mock_reddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_reddit_class.return_value = mock_reddit
        
        # Mock VADER
        with patch('data.reddit_sentiment.SentimentIntensityAnalyzer') as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer.polarity_scores.return_value = {'compound': 0.8}
            mock_analyzer_class.return_value = mock_analyzer
            
            scores = get_reddit_sentiment('AAPL', num_posts=1)
            assert len(scores) == 1
            assert scores[0] == 0.8

    @patch('data.reddit_sentiment.os.environ.get')
    @patch('data.reddit_sentiment.praw.Reddit')
    def test_get_reddit_sentiment_empty_results(self, mock_reddit_class, mock_env_get):
        """Test empty results from Reddit search."""
        mock_env_get.side_effect = lambda key, default='': 'test_id' if key == 'REDDIT_CLIENT_ID' else ('test_secret' if key == 'REDDIT_CLIENT_SECRET' else default)
        
        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = []
        
        mock_reddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_reddit_class.return_value = mock_reddit
        
        scores = get_reddit_sentiment('AAPL')
        assert scores == []

    @patch('data.reddit_sentiment.os.environ.get')
    @patch('data.reddit_sentiment.praw.Reddit')
    def test_get_reddit_sentiment_exception_handling(self, mock_reddit_class, mock_env_get):
        """Test that PRAW exceptions are caught and logged.
        
        Note: The current implementation catches exceptions during search(),
        but not during subreddit() call. This test verifies the current behavior.
        """
        mock_env_get.side_effect = lambda key, default='': 'test_id' if key == 'REDDIT_CLIENT_ID' else ('test_secret' if key == 'REDDIT_CLIENT_SECRET' else default)
        
        mock_subreddit = MagicMock()
        mock_subreddit.search.side_effect = Exception("Search API Error")
        
        mock_reddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_reddit_class.return_value = mock_reddit
        
        scores = get_reddit_sentiment('AAPL')
        assert scores == []  # Returns empty list on search error

    def test_vader_analyzer_import(self):
        """Test that VADER analyzer can be imported."""
        from data.reddit_sentiment import SentimentIntensityAnalyzer
        assert SentimentIntensityAnalyzer is not None