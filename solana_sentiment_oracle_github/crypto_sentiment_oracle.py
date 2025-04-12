
import random

def get_combined_sentiment():
    """
    Mock implementation: In a real-world scenario, this would aggregate data from
    CryptoPanic, Fear & Greed Index, Google Trends, on-chain metrics, etc.
    """
    sources = {
        "CryptoPanic": random.uniform(-1, 1),
        "FearGreedIndex": random.uniform(-1, 1),
        "GoogleTrends": random.uniform(-1, 1),
        "OnChainMetrics": random.uniform(-1, 1),
        "TechAnalysis": random.uniform(-1, 1),
    }

    weighted_score = sum(sources.values()) / len(sources)
    signal = "Buy" if weighted_score > 0.3 else "Sell" if weighted_score < -0.3 else "Hold"

    return {
        "score": round(weighted_score, 3),
        "signal": signal,
        "sources": {k: round(v, 3) for k, v in sources.items()}
    }

# Alias to match expected import in app.py
aggregate_sentiment = get_combined_sentiment
