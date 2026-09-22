from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Sequence

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


def _ensure_vader():
    try:
        nltk.data.find("sentiment/vader_lexicon")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)


def normalize_score(value: float, min_value: float = -1.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def compute_retail_sentiment(reddit_posts: Sequence[Dict[str, Any]] | Iterable[Dict[str, Any]]) -> float:
    _ensure_vader()
    analyzer = SentimentIntensityAnalyzer()

    texts: List[str] = []
    for post in reddit_posts:
        title = str(post.get("title", "")).strip()
        body = str(post.get("text", "")).strip()
        combined = " ".join(part for part in [title, body] if part)
        if combined:
            texts.append(combined)

    if not texts:
        return 0.0

    scores = []
    for text in texts:
        cleaned = re.sub(r"\s+", " ", text)
        scores.append(analyzer.polarity_scores(cleaned)["compound"])

    return normalize_score(float(sum(scores) / len(scores)))


def compute_price_momentum_score(pct_change: float, cap: float = 0.10) -> float:
    if cap <= 0:
        raise ValueError("cap must be positive.")
    return normalize_score(pct_change / cap)


def build_scores(reddit_posts: Sequence[Dict[str, Any]] | Iterable[Dict[str, Any]], pct_change: float) -> Dict[str, float]:
    return {
        "retail_sentiment_score": compute_retail_sentiment(reddit_posts),
        "price_momentum_score": compute_price_momentum_score(pct_change),
    }
