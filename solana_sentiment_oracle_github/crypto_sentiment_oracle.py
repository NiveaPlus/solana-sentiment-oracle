
# crypto_sentiment_oracle.py (fixed with proper Buy/Hold/Sell output)

def aggregate_sentiment():
    # Example mock scores from each source (replace with real data fetch)
    source_scores = {
        "CryptoPanic": -0.718,
        "FearGreedIndex": -0.427,
        "GoogleTrends": 0.614,
        "OnChainMetrics": 0.569,
        "TechAnalysis": 0.62
    }

    # Combine all scores into a single weighted score
    final_score = sum(source_scores.values()) / len(source_scores)

    # Convert final_score into Buy/Hold/Sell percentages
    if final_score > 0.33:
        sentiment = {
            "Buy": int(final_score * 100),
            "Hold": int((1 - final_score) * 100),
            "Sell": 0
        }
    elif final_score < -0.33:
        sentiment = {
            "Buy": 0,
            "Hold": int((1 + final_score) * 100),
            "Sell": int(-final_score * 100)
        }
    else:
        sentiment = {
            "Buy": int((final_score + 0.33) * 50),
            "Hold": int((1 - abs(final_score)) * 100),
            "Sell": int((0.33 - final_score) * 50)
        }

    # Add extra debug info
    sentiment["score"] = round(final_score, 3)
    sentiment["signal"] = "Buy" if final_score > 0.33 else "Sell" if final_score < -0.33 else "Hold"
    sentiment["sources"] = source_scores

    return sentiment
