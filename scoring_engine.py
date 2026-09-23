def normalize_sentiment(compound_scores: list[float]) -> float:
    """
    Averages per-post sentiment scores (each roughly -1..1, matching VADER's compound output),
    dampening confidence for small sample sizes. Clamps to [-1.0, 1.0].
    """
    if not compound_scores:
        return 0.0

    raw_sum = sum(compound_scores)
    count = len(compound_scores)
    average = raw_sum / count

    # Dampening confidence for small sample sizes
    # e.g., < 15 scores dampens toward 0
    trust_factor = min(1.0, count / 15.0)
    score = average * trust_factor

    return max(-1.0, min(1.0, score))


def normalize_price_momentum(percent_change: float, cap: float = 8.0) -> float:
    """
    Scales a raw percent price change to [-1.0, 1.0]; `cap` percent
    maps to full ±1.0, beyond that clamps rather than distorting scale.
    """
    score = percent_change / cap
    return max(-1.0, min(1.0, score))


def compute_divergence(retail_score: float, price_score: float, notable_threshold: float = 0.5) -> dict:
    """
    Returns retail_score, price_score, gap (retail_score - price_score),
    and a string label indicating the relationship.
    """
    gap = retail_score - price_score
    
    if abs(gap) < notable_threshold:
        label = "aligned"
    elif gap >= notable_threshold:
        label = "retail hotter than price"
    else:
        label = "price moving ahead of chatter"

    return {
        "retail_score": retail_score,
        "price_score": price_score,
        "gap": gap,
        "label": label
    }


if __name__ == "__main__":
    print("--- Sanity Check: Scoring Engine ---")
    
    # 1. Normalizing sentiment
    scores = [0.8, 0.9, -0.2, 0.4, 0.5]
    print(f"Sample scores: {scores}")
    print(f"Normalized Sentiment: {normalize_sentiment(scores):.2f}")
    
    # 2. Normalizing price momentum
    p_change = 4.0
    print(f"Price Momentum (4% change, 8% cap): {normalize_price_momentum(p_change):.2f}")
    
    # 3. Computing divergence
    r_score = 0.8
    p_score = 0.1
    d = compute_divergence(r_score, p_score)
    print(f"Divergence Label: {d['label']} (Gap: {d['gap']:.2f})")
