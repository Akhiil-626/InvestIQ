# InvestIQ — Reddit Sentiment vs. Price Divergence Tracker

InvestIQ is an educational tool (not a trading signal generator) that compares social media sentiment about a stock against its actual price movement. It flags when the two diverge significantly, teaching the difference between market hype and real price action.

## Tech Stack

- Flask (Python 3.11+)
- yfinance (real market data)
- PRAW (Reddit API - mocked by default until keys provided)
- vaderSentiment (Natural Language Processing)
- Grok API (xAI - for plain English summaries)

## Running Locally

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Environment configuration:
   Copy `.env.example` to `.env` and fill out your keys.

_Note: Sentiment data is mocked out of the box so you can run the app immediately. To enable real sentiment tracking, provide REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in the `.env` file._

3. Start the application:

```bash
flask run
# Or
python app.py
```

4. You can run tests using `pytest`:

```bash
pytest
```
