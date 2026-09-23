"""
ai_summary.py

Calls the Grok API (xAI) to turn the raw divergence numbers into a short,
beginner-friendly explanation. Framed strictly as education, never as
buy/sell advice.

If GROK_API_KEY is missing, or the API call fails for any reason (bad
key, network issue, rate limit), falls back to a plain sentence built
directly from the numbers so the results page never crashes because of
this module.
"""

import os
import requests

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-4.3"
REQUEST_TIMEOUT_SECONDS = 15

SYSTEM_PROMPT = (
    "You are an educational assistant helping a beginner investor "
    "understand a data signal. You are given a 'retail sentiment score' "
    "(how bullish/bearish social media chatter is) and a 'price momentum "
    "score' (how much the stock's price has actually moved), both on a "
    "-1.0 to +1.0 scale, plus a computed gap between them. "
    "Explain in 2-3 short sentences what this divergence means in plain "
    "English, for someone with no finance background. "
    "Do NOT give buy/sell advice, price targets, or predictions. "
    "Frame it purely as 'here's what the numbers show' education."
)


def _build_fallback_summary(ticker: str, retail_score: float, price_score: float, gap: float, label: str) -> str:
    """Plain-English summary built without calling any API, used when
    the Grok call isn't available for any reason."""
    if label == "aligned":
        return (
            f"For {ticker}, social sentiment ({retail_score:+.2f}) and price "
            f"momentum ({price_score:+.2f}) are roughly in line right now - "
            f"the online chatter matches what the price is actually doing."
        )
    if label == "retail hotter than price":
        return (
            f"For {ticker}, social sentiment ({retail_score:+.2f}) is running "
            f"noticeably hotter than the price momentum ({price_score:+.2f}) "
            f"supports. Chatter may be getting ahead of what's actually "
            f"happening to the price."
        )
    return (
        f"For {ticker}, the price momentum ({price_score:+.2f}) is moving "
        f"more than social sentiment ({retail_score:+.2f}) reflects. "
        f"The price is doing more than the online conversation suggests."
    )


def get_educational_summary(
    ticker: str,
    retail_score: float,
    price_score: float,
    gap: float,
    label: str,
) -> str:
    """
    Returns a short educational summary string. Always returns something
    usable - never raises - so a Grok outage never breaks the results page.
    """
    api_key = os.environ.get("GROK_API_KEY")

    if not api_key:
        return _build_fallback_summary(ticker, retail_score, price_score, gap, label)

    user_prompt = (
        f"Ticker: {ticker}\n"
        f"Retail sentiment score: {retail_score:+.2f}\n"
        f"Price momentum score: {price_score:+.2f}\n"
        f"Gap: {gap:+.2f}\n"
        f"Classification: {label}"
    )

    try:
        response = requests.post(
            GROK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROK_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.4,
                "max_tokens": 150,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except Exception as exc:
        # Catch-all is intentional here: this function must never raise,
        # since a Grok outage/bug should never break the results page.
        # Log the real reason for debugging, but always fall back cleanly.
        print(f"[ai_summary] Grok API call failed, using fallback: {exc}")
        return _build_fallback_summary(ticker, retail_score, price_score, gap, label)