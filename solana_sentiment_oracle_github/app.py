
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from crypto_sentiment_oracle import aggregate_sentiment
import altair as alt

st.set_page_config(page_title="Solana Sentiment Oracle", layout="wide")
st_autorefresh(interval=300000, key="refresh")  # 5 minutes

# Timeframe mapping
timeframes = {
    "1h": {"interval": "1m", "limit": 60},
    "3h": {"interval": "3m", "limit": 60},
    "8h": {"interval": "5m", "limit": 96},
    "24h": {"interval": "15m", "limit": 96},
    "3d": {"interval": "1h", "limit": 72},
    "7d": {"interval": "1h", "limit": 168},
    "1 month": {"interval": "4h", "limit": 180},
    "3 months": {"interval": "1d", "limit": 90},
    "1 year": {"interval": "1d", "limit": 365},
    "3 years": {"interval": "1d", "limit": 1095},
    "All": {"interval": "1d", "limit": 1500}
}

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

# UI
st.title("📊 Solana Sentiment Oracle")
st.markdown("Real-time Solana market sentiment and price trends")

selected_range = st.selectbox("Select Time Range", list(timeframes.keys()), index=3)
interval_info = timeframes[selected_range]
price_data = fetch_price_history(interval=interval_info["interval"], limit=interval_info["limit"])

# Sentiment
try:
    sentiment = aggregate_sentiment()
except Exception as e:
    st.error(f"Error fetching sentiment: {e}")
    sentiment = {"Buy": 0, "Hold": 100, "Sell": 0, "signal": "Hold"}

if "sentiment_history" not in st.session_state:
    st.session_state.sentiment_history = []

if "last_signal" not in st.session_state:
    st.session_state.last_signal = None

# Always log sentiment every 5 minutes
st.session_state.sentiment_history.append({
    "Time": datetime.now(),
    "Signal": sentiment.get("signal")
})
st.session_state.last_signal = sentiment.get("signal")

# Build sentiment DataFrame for dot plotting
dot_colors = {"Buy": "red", "Hold": "orange", "Sell": "green"}
dot_df = pd.DataFrame([
    entry for entry in st.session_state.sentiment_history
    if entry["Signal"] != "None"
])

# Match each dot with nearest available candle time
if not dot_df.empty:
    matched_dots = []
    for entry in dot_df.to_dict(orient="records"):
        match = price_data[price_data["Open time"] >= entry["Time"]]
        if not match.empty:
            row = match.iloc[0]
            matched_dots.append({
                "Open time": row["Open time"],
                "Close": row["Close"],
                "Signal": entry["Signal"],
                "Color": dot_colors.get(entry["Signal"], "gray")
            })
    dot_df = pd.DataFrame(matched_dots)
else:
    dot_df = pd.DataFrame(columns=["Open time", "Close", "Signal", "Color"])

# Layout
col1, col2 = st.columns([3, 1])

with col1:
    base = alt.Chart(price_data).mark_line().encode(
        x=alt.X("Open time:T", title="Time"),
        y=alt.Y("Close:Q", title="Price (USDT)")
    )

    if not dot_df.empty:
        dots = alt.Chart(dot_df).mark_point(size=100).encode(
            x="Open time:T",
            y="Close:Q",
            color=alt.Color("Signal:N", scale=alt.Scale(domain=["Buy", "Hold", "Sell"], range=["red", "orange", "green"]))
        )
        chart = base + dots
    else:
        chart = base

    st.altair_chart(chart.properties(height=400), use_container_width=True)

with col2:
    st.subheader("📊 Sentiment")
    st.metric("Buy %", f"{sentiment.get('Buy', 0)}%")
    st.metric("Hold %", f"{sentiment.get('Hold', 0)}%")
    st.metric("Sell %", f"{sentiment.get('Sell', 0)}%")
    st.progress(sentiment.get("Buy", 0) / 100)
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# Log table
history_df = pd.DataFrame([
    {"Time": entry["Time"].strftime("%H:%M:%S"), "Signal": entry["Signal"]}
    for entry in st.session_state.sentiment_history
])
if not history_df.empty:
    st.subheader("📉 Sentiment Signal History")
    st.dataframe(history_df.set_index("Time"))
