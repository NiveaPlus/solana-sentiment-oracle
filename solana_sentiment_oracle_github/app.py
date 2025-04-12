# app.py

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from crypto_sentiment_oracle import aggregate_sentiment

st.set_page_config(page_title="Solana Sentiment Oracle", layout="wide")

# -----------------------------
# AUTO-REFRESH EVERY 5 MINUTES
# -----------------------------
st_autorefresh(interval=300000, key="refresh")  # 300000 ms = 5 min

# -----------------------------
# UI CONFIG
# -----------------------------
time_ranges = {
    "1h": "1h",
    "3h": "3h",
    "8h": "8h",
    "24h": "1d",
    "3d": "3d",
    "7d": "7d",
    "1 month": "30d",
    "3 months": "90d",
    "1 year": "365d",
    "3 years": "1095d",
    "All": "max"
}

# -----------------------------
# FETCH PRICE DATA FROM BINANCE
# -----------------------------
def fetch_price_history(symbol="SOLUSDT", interval="1h", limit=200):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "Open time", "Open", "High", "Low", "Close", "Volume",
        "Close time", "Quote asset volume", "Number of trades",
        "Taker buy base", "Taker buy quote", "Ignore"])
    df["Open time"] = pd.to_datetime(df["Open time"], unit="ms")
    df["Close"] = df["Close"].astype(float)
    return df[["Open time", "Close"]]

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("📊 Solana Sentiment Oracle")
st.markdown("Real-time Solana market sentiment and price trends")

col1, col2 = st.columns([2, 1])

# Select time range for chart
with col1:
    selected_range = st.selectbox("Select Time Range", list(time_ranges.keys()), index=3)
    interval = "1d" if "year" in selected_range or selected_range == "All" else "1h"
    limit = 100 if interval == "1d" else 200
    price_data = fetch_price_history(interval=interval, limit=limit)
    st.line_chart(price_data.set_index("Open time"))

# Display current sentiment
with col2:
    sentiment = aggregate_sentiment()
    st.metric("Buy %", f"{sentiment['Buy']}%")
    st.metric("Hold %", f"{sentiment['Hold']}%")
    st.metric("Sell %", f"{sentiment['Sell']}%")
    st.progress(sentiment["Buy"] / 100)
    st.caption("Sentiment updates every 5 minutes")

# -----------------------------
# SENTIMENT HISTORY (LOCAL SESSION)
# -----------------------------
if "sentiment_history" not in st.session_state:
    st.session_state.sentiment_history = []

# Append current sentiment with timestamp
current_time = datetime.now().strftime("%H:%M:%S")
st.session_state.sentiment_history.append({
    "Time": current_time,
    "Buy": sentiment["Buy"],
    "Hold": sentiment["Hold"],
    "Sell": sentiment["Sell"]
})

# Show sentiment history chart
history_df = pd.DataFrame(st.session_state.sentiment_history)
st.subheader("📉 Sentiment History")
st.line_chart(history_df.set_index("Time"))
