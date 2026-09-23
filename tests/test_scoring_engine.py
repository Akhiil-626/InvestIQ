import pytest
from scoring_engine import normalize_sentiment, normalize_price_momentum, compute_divergence

def test_normalize_sentiment_normal():
    scores = [1.0] * 15 # Fully confident max score
    assert normalize_sentiment(scores) == 1.0
    
    scores_neg = [-1.0] * 15 # Fully confident min score
    assert normalize_sentiment(scores_neg) == -1.0
    
def test_normalize_sentiment_empty():
    assert normalize_sentiment([]) == 0.0

def test_normalize_sentiment_dampening():
    # Only 3 posts => trust factor is 3 / 15 = 0.2
    # Sum is 3.0, average is 1.0. Score = 1.0 * 0.2 = 0.2
    scores = [1.0, 1.0, 1.0]
    result = normalize_sentiment(scores)
    assert abs(result - 0.2) < 0.01

def test_normalize_sentiment_clamping():
    # If VADER somehow had a bug and returned values outside [-1, 1]
    scores = [2.0] * 20
    assert normalize_sentiment(scores) == 1.0
    scores = [-2.0] * 20
    assert normalize_sentiment(scores) == -1.0

def test_normalize_price_momentum_normal():
    assert normalize_price_momentum(4.0, cap=8.0) == 0.5
    assert normalize_price_momentum(-2.0, cap=4.0) == -0.5

def test_normalize_price_momentum_clamping():
    assert normalize_price_momentum(10.0, cap=8.0) == 1.0
    assert normalize_price_momentum(-50.0, cap=5.0) == -1.0

def test_compute_divergence_aligned():
    res = compute_divergence(0.1, 0.2, notable_threshold=0.5)
    assert res["label"] == "aligned"
    assert abs(res["gap"] - (-0.1)) < 0.01

def test_compute_divergence_hotter():
    res = compute_divergence(0.9, 0.1, notable_threshold=0.5)
    assert res["label"] == "retail hotter than price"
    assert abs(res["gap"] - 0.8) < 0.01

def test_compute_divergence_price_ahead():
    res = compute_divergence(-0.2, 0.4, notable_threshold=0.5)
    assert res["label"] == "price moving ahead of chatter"
    assert abs(res["gap"] - (-0.6)) < 0.01
