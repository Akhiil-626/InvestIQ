from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Optional

import praw
import yfinance as yf
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


def _get_reddit_client() -> Optional[praw.Reddit]:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "InvestIQ/0.1")

    if not client_id or not client_secret:
        return None

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def fetch_reddit_posts(
    ticker: str,
    subreddits: Optional[Iterable[str]] = None,
    limit: int = 25,
) -> List[Dict[str, Any]]:
    """Fetch recent Reddit posts relevant to a ticker from target subreddits."""
    subreddit_names = list(subreddits or ["wallstreetbets", "stocks"])
    ticker = ticker.strip().upper()
    reddit = _get_reddit_client()
    if reddit is None:
        return []

    posts: List[Dict[str, Any]] = []
    seen_ids = set()

    for subreddit_name in subreddit_names:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.search(query=ticker, sort="new", limit=limit):
                if submission.id in seen_ids:
                    continue
                seen_ids.add(submission.id)

                title = getattr(submission, "title", "")
                body = getattr(submission, "selftext", "")
                text = " ".join(part for part in [title, body] if part).strip()
                if not text:
                    continue

                posts.append(
                    {
                        "ticker": ticker,
                        "subreddit": subreddit_name,
                        "title": title,
                        "text": body[:4000] if body else "",
                        "url": getattr(submission, "url", ""),
                        "score": int(getattr(submission, "score", 0)),
                        "created_utc": getattr(submission, "created_utc", None),
                    }
                )
        except Exception:
            continue

    return posts


def fetch_market_history(ticker: str, period: str = "14d", interval: str = "1d") -> Dict[str, Any]:
    """Fetch recent market price history using yfinance."""
    symbol = ticker.strip().upper()
    stock = yf.Ticker(symbol)
    history = stock.history(period=period, interval=interval)

    if history.empty:
        raise ValueError(f"No market data returned for {symbol}.")

    history = history.reset_index()
    if "Date" in history.columns:
        history = history.rename(columns={"Date": "date"})
    history.columns = [str(col).strip().lower().replace(" ", "_") for col in history.columns]

    if "close" not in history.columns:
        raise ValueError(f"Market data for {symbol} does not contain a valid 'Close' column.")

    recent = history.tail(14).copy().sort_values("date")
    start_price = float(recent["close"].iloc[0])
    end_price = float(recent["close"].iloc[-1])
    pct_change = ((end_price - start_price) / start_price) if start_price else 0.0

    volume_total = float(recent["volume"].sum()) if "volume" in recent.columns else 0.0

    return {
        "ticker": symbol,
        "period": period,
        "interval": interval,
        "start_date": recent["date"].iloc[0],
        "end_date": recent["date"].iloc[-1],
        "pct_change": pct_change,
        "volume_total": volume_total,
        "avg_volume": float(volume_total / len(recent)) if len(recent) else 0.0,
        "history": recent.to_dict(orient="records"),
    }


def fetch_ticker_snapshot(ticker: str) -> Dict[str, Any]:
    return {
        "ticker": ticker.upper(),
        "reddit_posts": fetch_reddit_posts(ticker=ticker),
        "market": fetch_market_history(ticker=ticker),
    }


if __name__ == "__main__":
    sample = fetch_ticker_snapshot("AAPL")
    print(sample["ticker"])
    print("Reddit posts:", len(sample["reddit_posts"]))
    print("14d pct change:", round(sample["market"]["pct_change"], 4))
