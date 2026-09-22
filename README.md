# InvestIQ — Transparent Retail vs. Price Divergence Engine

InvestIQ is an educational stock-analysis project that compares social-media hype with real price movement. Instead of acting like a black-box trading signal generator, it focuses on transparency, explainability, and learning.

## Project Goal

The tool analyzes:

- Reddit sentiment around a stock ticker
- recent price movement over a 14-day window
- the gap between crowd sentiment and actual market performance

This helps investors ask an important question:

> Are people getting excited because the stock is genuinely moving, or is the narrative outrunning the market?

## Core Formula

The system computes:

- Retail sentiment score: $S_{retail} \in [-1.0, +1.0]$
- Price momentum score: $S_{price} \in [-1.0, +1.0]$
- Divergence score: $D = S_{retail} - S_{price}$

A positive divergence suggests hype may be stronger than the price trend. A negative divergence suggests prices may be moving without matching sentiment.

## Architecture

### 1. Data pipeline
File: `data_pipeline.py`

- fetches Reddit posts using `praw`
- searches subreddits such as `r/wallstreetbets` and `r/stocks`
- fetches recent market history using `yfinance`
- calculates 14-day percentage change and aggregate volume

### 2. Scoring engine
File: `scoring_engine.py`

- uses VADER sentiment analysis on Reddit titles and text
- normalizes sentiment into a score between -1.0 and +1.0
- converts price percentage change into a momentum score on the same scale

### 3. Divergence engine
File: `divergence_engine.py`

- computes the divergence signal
- classifies it as a hype bubble risk, quiet breakout, or balanced sentiment
- sends the signal and raw snippets to the Grok API for educational explanation

### 4. UI layer
File: `app.py`

- uses Streamlit to input a ticker
- shows Reddit snippets and price charts
- renders sentiment, momentum, and divergence values
- displays a beginner-friendly Grok summary

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your API keys in `.env`:

```env
GROK_API_KEY=your_grok_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=InvestIQ/0.1
```

4. Run the app:

```bash
streamlit run app.py
```

## Files in this project

- `data_pipeline.py`
- `scoring_engine.py`
- `divergence_engine.py`
- `app.py`
- `requirements.txt`
- `.env`
- `Preprocessing/` (legacy notebook prototype)

## Why this project is useful

InvestIQ is designed as a learning tool rather than a guaranteed profit system. It encourages critical thinking about:

- how social sentiment can outpace real price action
- why hype and fundamentals may diverge
- how to read market narratives more carefully

## Summary

This project turns the old ML stock prediction skeleton into a more transparent and educational market signal explorer. It mixes public Reddit sentiment, real price data, and AI-generated explanations to help users understand divergence between crowd behavior and actual performance.


