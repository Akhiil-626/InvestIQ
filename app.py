import os

from flask import Flask, render_template, request

from backend.data_pipeline import fetch_market_history, fetch_reddit_posts
from backend.divergence_engine import classify_divergence, compute_divergence, explain_divergence
from backend.scoring_engine import build_scores

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    ticker = "AAPL"
    result = None
    if request.method == "POST":
        ticker = request.form.get("ticker", "AAPL").strip().upper()
        try:
            reddit_posts = fetch_reddit_posts(ticker=ticker)
            market_data = fetch_market_history(ticker=ticker)
            scores = build_scores(reddit_posts, market_data["pct_change"])
            divergence = compute_divergence(
                scores["retail_sentiment_score"],
                scores["price_momentum_score"],
            )
            explanation = explain_divergence(
                ticker=ticker,
                reddit_posts=reddit_posts,
                market_stats=market_data,
                retail_score=scores["retail_sentiment_score"],
                price_score=scores["price_momentum_score"],
                divergence_score=divergence,
                api_key=os.getenv("GROK_API_KEY"),
            )
            result = {
                "ticker": ticker,
                "market": market_data,
                "reddit_posts": reddit_posts,
                "scores": scores,
                "divergence": divergence,
                "classification": classify_divergence(divergence),
                "explanation": explanation,
            }
        except Exception as exc:
            result = {"error": str(exc)}

    return render_template("index.html", result=result, ticker=ticker)


@app.route("/dashboard")
def dashboard():
    ticker = "AAPL"
    try:
        reddit_posts = fetch_reddit_posts(ticker=ticker)
        market_data = fetch_market_history(ticker=ticker)
        scores = build_scores(reddit_posts, market_data["pct_change"])
        divergence = compute_divergence(scores["retail_sentiment_score"], scores["price_momentum_score"])
        explanation = explain_divergence(
            ticker=ticker,
            reddit_posts=reddit_posts,
            market_stats=market_data,
            retail_score=scores["retail_sentiment_score"],
            price_score=scores["price_momentum_score"],
            divergence_score=divergence,
            api_key=os.getenv("GROK_API_KEY"),
        )
        result = {
            "ticker": ticker,
            "market": market_data,
            "reddit_posts": reddit_posts,
            "scores": scores,
            "divergence": divergence,
            "classification": classify_divergence(divergence),
            "explanation": explanation,
        }
    except Exception as exc:
        result = {"error": str(exc)}

    return render_template("dashboard.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
