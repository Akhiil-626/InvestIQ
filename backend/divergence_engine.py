from __future__ import annotations

import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


def compute_divergence(retail_score: float, price_score: float) -> float:
    return float(retail_score - price_score)


def classify_divergence(divergence_score: float) -> str:
    if divergence_score > 0.5:
        return "Hype bubble risk"
    if divergence_score < -0.5:
        return "Quiet breakout / value setup"
    return "Balanced sentiment"


def explain_divergence(
    ticker: str,
    reddit_posts: List[Dict[str, Any]],
    market_stats: Dict[str, Any],
    retail_score: float,
    price_score: float,
    divergence_score: float,
    api_key: str | None = None,
    model: str = "grok-2-latest",
) -> str:
    api_key = api_key or os.getenv("GROK_API_KEY")
    if not api_key:
        return "GROK_API_KEY is not configured. Add it to your .env file to enable educational explanations."

    snippets = []
    for post in reddit_posts[:5]:
        title = str(post.get("title", "")).strip()
        text = str(post.get("text", "")).strip()
        snippets.append(f"- {title}: {text[:250]}")

    prompt = f"""
You are an educational market analyst helping retail investors assess sentiment vs. price fundamentals.

Ticker: {ticker}
Retail sentiment score (S_retail): {retail_score:.3f}
Price momentum score (S_price): {price_score:.3f}
Divergence score: {divergence_score:.3f}
Price 14-day pct change: {market_stats.get('pct_change', 0.0):.4f}
Recent Reddit snippets:
{chr(10).join(snippets) if snippets else 'No Reddit snippets available.'}

Explain in beginner-friendly language why crowd sentiment and price may be diverging. Mention possible hype bubbles, quiet breakouts, and caution. End with 3 self-reflection questions investors should ask before reacting.
"""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]
    except Exception as exc:
        return f"Unable to generate Grok explanation: {exc}"
