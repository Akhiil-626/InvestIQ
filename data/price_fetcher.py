"""
price_fetcher.py

Wraps yfinance so the rest of the app doesn't need to know about its API
shape. Returns plain percent-change numbers that scoring_engine can consume.

Yahoo Finance's endpoints occasionally return an empty or non-JSON
response (rate limiting, bot detection, transient outage) instead of
raising a clean error - yfinance then fails with a raw JSONDecodeError.
_fetch_history() below retries a couple of times with a short backoff
and converts any such failure into a plain ValueError so routes never
have to deal with yfinance's internals directly.
"""

import time
import json
import yfinance as yf

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1.5


def _fetch_history(ticker: str, period: str):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            history = yf.Ticker(ticker).history(period=period)
            if not history.empty:
                return history
            last_error = ValueError(f"No price data found for '{ticker}'")
        except (json.JSONDecodeError, Exception) as exc:  # yfinance can raise several types here
            last_error = exc

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)

    # Give a message that actually explains what's going on, instead of
    # surfacing yfinance's internal JSONDecodeError to the user.
    raise ValueError(
        f"Couldn't fetch price data for '{ticker}' - Yahoo Finance may be "
        f"rate-limiting requests right now. Try again in a moment. "
        f"(underlying error: {last_error})"
    )


def get_price_momentum(ticker: str, days: int = 7) -> float:
    """
    Return the percent price change for `ticker` over the last `days`
    trading days, e.g. 4.3 for a +4.3% move.

    Raises ValueError if the ticker returns no data (bad symbol, delisted,
    Yahoo rate limiting, etc.) so the route can show a clean error instead
    of a stack trace.
    """
    history = _fetch_history(ticker, period=f"{days + 2}d")

    if len(history) < 2:
        raise ValueError(f"Not enough price data found for '{ticker}'")

    closes = history["Close"]
    start_price = closes.iloc[0]
    end_price = closes.iloc[-1]

    percent_change = ((end_price - start_price) / start_price) * 100
    return round(float(percent_change), 2)


def get_current_price(ticker: str) -> float:
    """Latest close price, used just for display on the results page."""
    history = _fetch_history(ticker, period="1d")
    return round(float(history["Close"].iloc[-1]), 2)