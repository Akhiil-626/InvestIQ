import os
import hashlib
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_mock_sentiment(ticker: str, num_posts: int = 15) -> list[float]:
    """
    Returns plausible fake per-post sentiment scores.
    Deterministically seeded on the ticker string so it's stable across refreshes.
    """
    seed_hash = int(hashlib.md5(ticker.upper().encode('utf-8')).hexdigest(), 16)
    
    # LCG random generator mapped to [-1, 1]
    scores = []
    current_seed = seed_hash
    for _ in range(num_posts):
        current_seed = (1103515245 * current_seed + 12345) % (2**31)
        val = (current_seed / (2**31 - 1)) * 2 - 1.0
        # Bias slightly toward positive for realism
        val = max(-1.0, min(1.0, val + 0.15))
        scores.append(val)
        
    return scores


def get_reddit_sentiment(ticker: str, num_posts: int = 25) -> list[float]:
    """
    Searches r/wallstreetbets, r/stocks, r/investing for the ticker via PRAW,
    and scores each post's title + body with VADER.
    """
    client_id = os.environ.get("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "").strip()
    
    if not client_id or not client_secret:
        raise NotImplementedError("Reddit credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET) missing from .env")
        
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="InvestIQ:v1.0 (by u/investiq_dev)"
    )
    
    analyzer = SentimentIntensityAnalyzer()
    scores = []
    
    subreddits = reddit.subreddit("wallstreetbets+stocks+investing")
    search_query = f"{ticker.upper()}"
    
    try:
        submissions = subreddits.search(search_query, limit=num_posts)
        for submission in submissions:
            text = f"{submission.title} {submission.selftext}"
            metrics = analyzer.polarity_scores(text)
            scores.append(metrics['compound'])
    except Exception as e:
        print(f"PRAW Search Error: {e}")
        
    return scores
