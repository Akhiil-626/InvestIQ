import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

from scoring_engine import normalize_sentiment, normalize_price_momentum, compute_divergence
from data.price_fetcher import get_price_momentum, get_current_price
from data.reddit_sentiment import get_mock_sentiment, get_reddit_sentiment
from data.ai_summary import get_educational_summary

load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_post():
    ticker = request.form.get("ticker", "").strip().upper()
    if not ticker:
        return render_template("index.html", error="Please provide a valid ticker.")
    return redirect(url_for("analyze_get", ticker=ticker))

@app.route("/analyze/<ticker>", methods=["GET"])
def analyze_get(ticker):
    try:
        ticker = ticker.upper()
        # Fetch real price data
        price_perc = get_price_momentum(ticker)
        curr_price = get_current_price(ticker)
        
        has_real_sentiment = False
        try:
            raw_sentiment = get_reddit_sentiment(ticker)
            has_real_sentiment = True
        except NotImplementedError:
            raw_sentiment = get_mock_sentiment(ticker)
            
        r_score = normalize_sentiment(raw_sentiment)
        p_score = normalize_price_momentum(price_perc)
        
        div = compute_divergence(r_score, p_score)
        
        summary = get_educational_summary(
            ticker=ticker,
            retail_score=div["retail_score"],
            price_score=div["price_score"],
            gap=div["gap"],
            label=div["label"]
        )
        
        return render_template(
            "results.html",
            ticker=ticker,
            current_price=curr_price,
            price_change=price_perc,
            retail_score=div["retail_score"],
            price_score=div["price_score"],
            gap=div["gap"],
            label=div["label"],
            summary=summary,
            has_real_sentiment=has_real_sentiment
        )
        
    except ValueError as e:
        return render_template("index.html", error=str(e)), 404
    except Exception as e:
        return render_template("index.html", error=f"An unexpected error occurred: {str(e)}"), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
